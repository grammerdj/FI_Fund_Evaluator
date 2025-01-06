"""
Import Statements Necessary for Dataframe Exporting into Excel Documents
"""
import os
import pandas as pd
from datetime import datetime as dt
# -------------------------------------------#
"""
Class: Formatter
Purpose: To export the fund history and performance tables as excel documents
"""
class Formatter():

    def __init__(self, ticker, output_config, summary_config, history_df, reinvestment_df, performance_df):
        """
        Initializing the attributes of the class
        """
        # Dataframe Attributes
        self.hist = history_df
        self.reinv = reinvestment_df
        self.perf = performance_df

        # Output Attributes
        self.date = dt.strftime(dt.date(dt.now()), "%Y_%m_%d")
        self.loc = output_config["location"]
        self.prefix = output_config["prefix"]
        self.ext = output_config["extension"]
        self.name = f"{self.prefix}{ticker}-specs-{self.date}{self.ext}"
        self.path = os.path.join(self.loc, self.name)

        
        # Summary attributes 
        self.sumloc = summary_config["location"]
        self.sumprefix = summary_config["prefix"]
        self.sumext = summary_config["extension"]
        self.sumname = f"{self.sumprefix}{self.date}{self.sumext}"
        self.sumpath = os.path.join(self.sumloc, self.sumname)

# -------------------------------------------#

    def output_excel(self, start_date, seed_capital, req_ret):
        """
        Outputs an Excel Document with the current naming convention `Ticker`-specs-`date`.xlsx into the output location specified in the config.
        Sheets:
            History - contains history_df
            Reinvestment_`start_date`_`seed_capital` - contains reinvestment_df
            Performance_`req_ret` - contains performance_df
        """
        # Creating the excel document
        with pd.ExcelWriter(self.path,
                            date_format="YYYY-MM-DD",
                            datetime_format="YYYY-MM-DD"
        ) as writer:
            
            self.hist.to_excel(writer, sheet_name = "History")
            self.reinv.to_excel(writer, sheet_name = f"Reinvestment_{start_date.replace('/','-')}_{seed_capital}", index=False)
            self.perf.to_excel(writer, sheet_name = f"Performance_{req_ret}", index=False)

# -------------------------------------------#

    def output_summary(self, summary_df, less_one_year, optimized):
        """
        Outputs a summary excel document containing each ticker's longest running geometric return and the number of full years of return data.
        """

        with pd.ExcelWriter(self.sumpath,
                            date_format="YYYY-MM-DD",
                            datetime_format="YYYY-MM-DD"
        ) as writer:
            
            summary_df.to_excel(writer, sheet_name = "Performance Summary", index=False)
            less_one_year.to_excel(writer, sheet_name = "Funds Started < 1 Year Ago", index=False)
            optimized.to_excel(writer, sheet_name = 'Optimized Portfolio Attributes', index=False)


