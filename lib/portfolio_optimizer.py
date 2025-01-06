"""
Import Statements Necessary for Optimization of FI Portfolio
"""
import pandas as pd
import numpy as np
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import objective_functions
# -------------------------------------------#
"""
Class: portfolioOptimizer
Purpose: To find the optimized weights of funds ran through the fund_returns program to acheive the maximum Sharpe Ratio
"""
class portfolioOptimizer():

    def __init__(self, rf_rate):

        # Initializing Attributes
        self.rf_rate = rf_rate/100
        self.weights = pd.DataFrame()
        self.strategy = list()
        self.return_list = list()
        self.risk = list()
        self.sharpe = list()

# -------------------------------------------#

    def maximize_Sharpe(self, return_df, cov_df, summary_path):
        """
        Optimizes portfolio weights for the maximum Sharpe ratio,
        """
        # Creating EfficientFrontier Instance and Calculating Weights
        ef = EfficientFrontier(return_df, cov_df)
        ef.add_objective(objective_functions.L2_reg)
        ef.max_sharpe(risk_free_rate = self.rf_rate)

        # Cleaning and Saving Weights
        ef.clean_weights()
        ef.save_weights_to_file(summary_path)

        # Getting Optimized Portfolio Performance
        expected_return, volatility, sharpe = ef.portfolio_performance(risk_free_rate=self.rf_rate)
        self.strategy.append('Max. Sharpe')
        self.return_list.append(expected_return)
        self.risk.append(volatility)
        self.sharpe.append(sharpe)

# -------------------------------------------#

    def maximize_return(self, return_df, cov_df, summary_path, req_vol):
        """
        Optimizes porfolio weights to acheive a maximum return with a given required variance.
        """
        # Creating EfficientFrontier Instance and Calculating Weights
        ef = EfficientFrontier(return_df, cov_df)
        ef.add_objective(objective_functions.L2_reg)
        ef.efficient_risk(req_vol/100)

        # Cleaning and Saving Weights
        ef.clean_weights()
        ef.save_weights_to_file(summary_path)

        # Getting Optimized Portfolio Performance
        expected_return, volatility, sharpe = ef.portfolio_performance(risk_free_rate=self.rf_rate)
        self.strategy.append(f'Max. Ret w/ Required Var = {req_vol}')
        self.return_list.append(expected_return)
        self.risk.append(volatility)
        self.sharpe.append(sharpe)

# -------------------------------------------#

    def minimize_volatility(self, return_df, cov_df, summary_path, req_ret):
        """
        Optimizes portfolio weights to achieve a minimum volatility given a required return.
        """
        # Creating EfficientFrontier Instance and Calculating Weights
        ef = EfficientFrontier(return_df, cov_df)
        ef.add_objective(objective_functions.L2_reg)
        ef.efficient_return(req_ret/100)

        # Cleaning and Saving Weights
        ef.clean_weights()
        ef.save_weights_to_file(summary_path)

        # Getting Optimized Portfolio Performance
        expected_return, volatility, sharpe = ef.portfolio_performance(risk_free_rate=self.rf_rate)
        self.strategy.append(f'Min. Vol w/ Required Ret = {req_ret}')
        self.return_list.append(expected_return)
        self.risk.append(volatility)
        self.sharpe.append(sharpe)

    