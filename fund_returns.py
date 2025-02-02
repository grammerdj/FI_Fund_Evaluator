"""
Script that takes in configuration and outputs excel documents with the following three sheets:
    - Fund Metrics (monthly price and dividend data)
    - Reinvestment Data
    - Fund Performance
"""
from lib.config import Config
from lib.scraper import Scraper
from lib.parser import Parser
from lib.formatter import Formatter
from lib.portfolio_optimizer import portfolioOptimizer
import os
import sys
import traceback
import pandas as pd
import numpy as np
import math
import logging
from datetime import datetime as dt

# -------------------------------------------#

# Step 0: Initialize Logger

## Getting Current Date and Time
datetime = dt.strftime(dt.now(), "%Y%m%d_%H%M%S")
logger = logging.getLogger(__name__)
log_file_path = os.path.join("__LOG DIR PATH__", f'fund_return_log_{datetime}.log')
logging.basicConfig(encoding='utf-8',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    format = '%(asctime)s - %(levelname)s: %(message)s',
                    handlers=[logging.FileHandler(log_file_path)],
                    level=logging.INFO)

# Step 1: Call Configuration Class

logger.info("Step 1 Begins - Loading in Configuration")
try:
    config = Config()
    config.get_config()
except Exception as e:
    logger.error(f"Step 1 failed with the following message - {traceback.format_exc()}")
    sys.exit(1)

# Step 2: Read in Input Metrics

logger.info("Step 2 Begins - Verifying and Reading Input File")
try:
    input_dir = config.input_cfg["location"]

    ## Checking Number of Files
    assert len(os.listdir(input_dir)) == 1, "Too many input files in the directory"

    ## Checking File Naming Convention
    input_file = os.listdir(input_dir)[0]
    assert input_file[:len(config.input_cfg["prefix"])] == config.input_cfg["prefix"], "Naming Convention is Incorrect"
    assert input_file[-len(config.input_cfg["extension"]):] == config.input_cfg["extension"], "Naming Convention is Incorrect"

    ## Reading in Input File
    input_path = os.path.join(input_dir, input_file)
    fund_tickers = pd.read_excel(input_path)["Tickers"].tolist()

except Exception as e:
    logger.error(f"Step 2 failed with the following message - {traceback.format_exc()}")
    sys.exit(1)

# Step 3: Loop Through Tickers


logger.info("Step 3 Begins - Getting Fund Return Metrics")
try: 
    ## Date Information
    cd = dt.now().year
    sd = dt.strptime(config.func_args["start_dt"], "%d/%m/%Y").year

    ## Summary Data Lists/DFs
    tickers = list()
    geom_ret = list()
    std_ret = list()
    years = list()
    forward_div_rate = list()
    forward_div_yield = list()
    curr_price = list()
    less_than_one = list()

    ## Preparing for Portfolio Analysis
    i = np.arange(sd, cd, 1)
    yearly_ret = pd.DataFrame(index=i)

    ## Calculating per-fund perfomance 
    for ticker in fund_tickers:
        scrape = Scraper()
        scrape.get_data(ticker)
        parse = Parser(scrape.ticker, scrape.prices)
        parse.get_monthly_data()
        parse.get_reinvestment_metrics(config.func_args["start_cap"], config.func_args["start_dt"])
        parse.get_performance(config.func_args["req_ret"])
        formatting = Formatter(ticker, config.output_cfg, config.summary_cfg, parse.monthly_data, parse.reinvestment_data, parse.investment_performance)
        formatting.output_excel(config.func_args["start_dt"], config.func_args["start_cap"], config.func_args["req_ret"])

        ## Adding to Summary Data Lists
        if parse.investment_performance.shape[0] > 1:
            tickers.append(ticker)
            geom_ret.append(round(float(parse.investment_performance["Geometric Return w/ Reinvestment"][-1:].values[0]), 4))
            std_ret.append(round(float(parse.investment_performance["Rate w/ Reinvestment"].std()/100), 4))
            years.append(int(parse.investment_performance["Geometric Return w/ Reinvestment"].count()))
            forward_div_rate.append(scrape.ticker.info["dividendRate"])
            forward_div_yield.append(round(scrape.ticker.info["dividendYield"], 4))
            curr_price.append(scrape.prices["Close"][-1:].values[0])
            n = parse.investment_performance["Rate w/ Reinvestment"].to_numpy()[1:]/100
            temp_df = pd.DataFrame({ticker: np.hstack((np.zeros(len(i)-len(n)) + np.nan, n))})
            yearly_ret = pd.concat([yearly_ret, temp_df], axis=1) 
        else:
            less_than_one.append(ticker)


    ## Calculating Optimal Portfolios
    cov_df = yearly_ret.cov()
    ret_df = pd.Series(geom_ret, index = tickers)
    opt = portfolioOptimizer(config.func_args["rf_rate"])

    ### File Paths
    sharpe_weight_path = os.path.join(formatting.sumloc, f"sharpe-optimal-weights-{formatting.date}.csv")
    vol_weight_path = os.path.join(formatting.sumloc, f"req-vol-optimal-weights-{formatting.date}.csv")
    ret_weight_path = os.path.join(formatting.sumloc, f"req-ret-optimal-weights-{formatting.date}.csv")

    ### Optimizing
    sharpe_weights = opt.maximize_Sharpe(ret_df, cov_df)
    max_ret_weights = opt.maximize_return(ret_df, cov_df, config.func_args["opt_vol"])
    min_vol_weights = opt.minimize_volatility(ret_df, cov_df, config.func_args["opt_ret"])
    weights_dict = {"Sharpe - ":sharpe_weights, "Max Return - ": max_ret_weights, "Min Volatility - ": min_vol_weights}

    ### Formatting Performance
    optimized = pd.DataFrame({'Strategy':opt.strategy, 'Portfolio Return':opt.return_list, 'Portfolio Volatility':opt.risk, 'Portfolio Sharpe':opt.sharpe})

    ## Formatting summary dataframes
    summary_df = pd.DataFrame({"Ticker": tickers,
                               "Geometric Return": geom_ret,
                               "Standard Deviation of Returns": std_ret,
                               "Number of Full Years": years,
                               "Current Price": curr_price,
                               "Annual Dividend Amt": forward_div_rate,
                               "Current Annual Dividend Yield": forward_div_yield})
    less_one_year = pd.DataFrame({"Ticker":less_than_one})

    for di in weights_dict:
        df = weights_dict[di]
        summary_df = pd.merge(summary_df, df, on='Ticker')
        summary_df[di+"$ invested"] = summary_df[di.split("-")[0] + "Weights"] * config.func_args["port_cap"]
        summary_df[di+"Num Shares"] = summary_df.apply(lambda x: math.trunc(x[di+"$ invested"] / x["Current Price"]), axis=1)
        summary_df[di+"Annual Dividend"] = summary_df.apply(lambda x: round(x["Annual Dividend Amt"] * x[di+"Num Shares"], 2), axis=1)

    ## Saving Configuration Snapshot
    config_wide = pd.DataFrame(config.func_args, index=[0])
    config_wide["id"] = config_wide.index
    config_long = config_wide.melt(id_vars='id', var_name = "Configuration", value_name = "Value").drop("id", axis=1)

    ## Save Summary File
    formatting.output_summary(summary_df, optimized, less_one_year, config_long)

except Exception as e:
    logger.error(f"Step 3 failed with the following message - {traceback.format_exc()}")
    sys.exit(1)

logger.info("Script Finished. Have a nice day!")


