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
import os
import sys
import traceback
import pandas as pd
import logging
from datetime import datetime as dt

# -------------------------------------------#

# Step 0: Initialize Logger

## Getting Current Date and Time
datetime = dt.strftime(dt.now(), "%Y%m%d_%H%M%S")
logger = logging.getLogger(__name__)
log_file_path = os.path.join("__LOG DIRECTORY__", f'fund_return_log_{datetime}.log')
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
    ## Summary Data Lists
    tickers = []
    geom_ret = []
    years = []
    for ticker in fund_tickers:
        scrape = Scraper()
        scrape.get_data(ticker)
        parse = Parser(scrape.ticker, scrape.prices)
        parse.get_monthly_data()
        parse.get_reinvestment_metrics(config.func_args["start_cap"], config.func_args["start_dt"])
        parse.get_performance(config.func_args["req_ret"])
        formatting = Formatter(ticker, config.output_cfg, parse.monthly_data, parse.reinvestment_data, parse.investment_performance)
        formatting.output_excel(config.func_args["start_dt"], config.func_args["start_cap"], config.func_args["req_ret"])

        ## Adding to Summary Data Lists
        tickers.append(ticker)
        geom_ret.append(round(float(parse.investment_performance["Geometric Return w/ Reinvestment"][-1:].values[0]), 4))
        years.append(int(parse.investment_performance["Geometric Return w/ Reinvestment"].count()))

    ## Save Summary File
    summary_df = pd.DataFrame({"Ticker":tickers,
                               "Geometric Return": geom_ret,
                               "Number of Full Years": years})
    formatting.output_summary(config.summary_cfg, summary_df)

except Exception as e:
    logger.error(f"Step 3 failed with the following message - {traceback.format_exc()}")
    sys.exit(1)

logger.info("Script Finished. Have a nice day!")


