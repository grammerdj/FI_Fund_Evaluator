"""
Import Statements Necessary for yfinance Ticker Object Capital Gains and Dividend Extraction
"""
import pandas as pd
from datetime import datetime as dt
import numpy as np
import copy
from statistics import geometric_mean
# -------------------------------------------#
"""
Class: Parser
Purpose: To extract the capital gains and dividend history from a yfinance Ticker object
"""
class Parser():

    def __init__(self, ticker_object, prices):
        """
        Initializing the attributes of the class
        """
        # Datetime attributes
        self.now = dt.now()
        self.current = pd.DataFrame.from_dict({"Year": [self.now.year], "Month": [self.now.month]})
        # Attribute Placeholders
        self.ticker_object = ticker_object
        self.prices = prices
        self.dividends = pd.DataFrame(self.ticker_object.dividends)
        self.monthly_data = pd.DataFrame()
        self.reinvestment_data = pd.DataFrame()
        self.return_metrics = pd.DataFrame

# -------------------------------------------#

    def get_monthly_data(self):
        """
        Parses Ticker Object Information into a table with the following columns:
            - Date (1st of month)
            - Open (1st of month)
            - High (within month)
            - Low (within month)
            - Close (last of month)
            - Adj Close (last of month)
            - Volume (montly total)
            - Prev Div Date (Most recent monthly dividend in the given month)
            - Div (total monthly dividend value)
        Filtering Logic:
            - Removes first month if incomplete (starts > 4 days into the month)
            - Removes current month
        """
    
        # Step 1: Extract and parse price data
        price = copy.deepcopy(self.prices)
        price.reset_index(inplace=True)

        ## Create Time Columns
        price['Day'] = price['Date'].apply(lambda x: x.day)
        price['Month'] = price['Date'].apply(lambda x: x.month)
        price["Year"] = price['Date'].apply(lambda x: x.year)
        price.drop(columns=['Date'], inplace=True)

        ## Filter Months
        if price.groupby(["Year", "Month"])[["Year", "Month", "Day"]].min()["Day"].iloc[0] > 4:
            price = price.loc[(price["Year"] != price["Year"].iloc[0]) | (price["Month"] != price["Month"].iloc[0])]
        price = price.loc[(price["Year"] != self.current["Year"].iloc[0]) | (price["Month"] != self.current["Month"].iloc[0])]

        ## Group By Month and Year
        price_gp = price.groupby(['Year', 'Month'])
        price.set_index(['Year', 'Month'], inplace=True)
        price["Open"] = price_gp[["Open"]].first()
        price["High"] = price_gp[["High"]].max()
        price["Low"] = price_gp[["Low"]].min()
        price["Close"] = price_gp[["Close"]].last()
        price["Adj Close"] = price_gp[["Adj Close"]].last()
        price["Volume"] = price_gp["Volume"].sum()
        price["Day_Begin"] = price_gp["Day"].first()
        price.drop(columns=["Day"], inplace=True)
        price.drop_duplicates(inplace=True)

        # Step 2: Extract and Parse Dividend Data
        div = copy.deepcopy(self.dividends)
        div.reset_index(inplace=True)

        ## Create Time Columns
        div['Day'] = div['Date'].apply(lambda x: x.day)
        div['Month'] = div['Date'].apply(lambda x: x.month)
        div["Year"] = div['Date'].apply(lambda x: x.year)
        div.drop(columns=['Date'], inplace=True)

        ## Filter Months
        div = div.loc[(div["Year"] != self.current["Year"].iloc[0]) | (div["Month"] != self.current["Month"].iloc[0])]
        if (price.index[0][0] + ((price.index[0][1])/12)) > (div["Year"].iloc[0] + ((div["Month"].iloc[0])/12)):
            div = div.loc[(div["Year"] + ((div["Month"])/12)) >= (price.index[0][0] + ((price.index[0][1])/12))]

        ## Group By Month and Year
        div_gp = div.groupby(["Year", "Month"])
        div.set_index(['Year', 'Month'], inplace=True)
        div["Day_Div"] = div_gp["Day"].last()
        div["Dividends"] = div_gp["Dividends"].sum()
        div.drop(columns=["Day"], inplace=True)
        div.drop_duplicates(inplace=True)

        # Step 3: Join and Format
        joined = pd.concat([price, div], axis = 1, join="outer")
        joined.reset_index(inplace=True)
        joined["Date"] = joined.apply(lambda x: dt.strptime("/".join([str(round(x['Year'])), str(round(x['Month'])), str(round(x["Day_Begin"]))]), "%Y/%m/%d"), axis=1)
        joined["Prev Div Date"] = joined.apply(lambda x: dt.strptime("/".join([str(round(x['Year'])), str(round(x['Month'])), str(round(x["Day_Div"]))]), "%Y/%m/%d")  if not (np.isnan(x["Day_Div"])) else pd.NaT, axis=1)
        joined.set_index("Date", inplace=True)
        joined.drop(columns = ["Year", "Month", "Day_Div", "Day_Begin"], inplace=True)
        cols = joined.columns.tolist()
        cols = cols[:-2] +cols[-1:]+ cols[-2:-1]
        joined = joined[cols]
        self.monthly_data = joined

        ## Clean Memory
        del joined
        del price
        del price_gp
        del div
        del div_gp
# -------------------------------------------#

    def get_reinvestment_metrics(self, start_val, start_date):
        """
        Calculates reinvestment tables given a start_val and start_date. Returns the following columns:
            - Date
            - Reinvestment $
            - Num Shares Reinvestment
            - Cumulative Value
            - Ending Shares
        """


        # Re-establishing Price and Dividend Table
        div = copy.deepcopy(self.dividends)
        price = copy.deepcopy(self.prices)

        # Step 1: Find Starting Amount and Date, Locate Initial Share Price and First Dividend
        self.start =  dt.strptime(start_date, "%m/%d/%Y")
        td_zero = pd.Timedelta(0)

        ## Starting Price and Shares
        p_arr = np.array(price.index.tolist()) - self.start
        p_idx = min(np.where(p_arr >= td_zero)[0])
        self.start_date = price.iloc[p_idx].name
        self.start_shares = np.trunc(start_val / price["Close"].iloc[p_idx])
        self.start_val = self.start_shares*price["Close"].iloc[p_idx]

        ## Truncating Dividends to Dividends After Start Date
        self.start_tz = self.start.replace(tzinfo=div.index.tolist()[0].tzinfo)
        d_arr = np.array(div.index.tolist()) - self.start_tz
        d_idx = min(np.where(d_arr > td_zero)[0])
        div = div.iloc[d_idx:]
        div.reset_index(inplace=True)

        ## Gathering Monthly Data 

        # Step 2: Looping Through the Months and Collecting Returns for Each Month
        
        ## Filtering Monthly Data
        monthly_data = copy.deepcopy(self.monthly_data)
        monthly_data.reset_index(inplace=True)
        filter = monthly_data.apply(lambda x: (x["Date"].year + (x["Date"].month/12)) >= (self.start_date.year + (self.start_date.month/12)), axis=1)
        monthly_data = monthly_data.loc[filter]
        monthly_data.reset_index(inplace=True, drop = True)

        ## Column Lists
        date_l = []
        div_l = []
        shares_l = []
        end_l = []
        val_l = []


        ## Looping Through Dividend Payments Per Month
        for idx in monthly_data.index.tolist():
            
            # Date
            date = monthly_data.iloc[idx]["Date"]
        
            # Dividend Value, Shares Purchased
            div_filter = div.apply(lambda x: (x["Date"].year == date.year) & (x["Date"].month == date.month), axis=1)
            monthly_div = div.loc[div_filter]
            dividend_val = 0
            shares_purchased = 0
            if monthly_div.shape[0] != 0:
                for row in range(0, monthly_div.shape[0]):
                    div_row = monthly_div.iloc[row]
                    if idx == 0:
                        dividend_val += div_row["Dividends"]*self.start_shares
                    else: 
                        dividend_val += div_row["Dividends"]*end_l[idx-1]
                    timestamp = pd.Timestamp(dt.date(div_row["Date"]))
                    shares_purchased += dividend_val/price.loc[timestamp]["Close"]

            # Ending Shares
            if idx == 0:
                ending_shares = shares_purchased + self.start_shares
            else:
                ending_shares = shares_purchased + end_l[idx-1]

            # Month-End Value

            month_end_val = monthly_data.iloc[idx]["Close"]*ending_shares

            # Appending the Lists
            date_l.append(date)
            div_l.append(round(dividend_val, 2))
            shares_l.append(round(shares_purchased, 2))
            end_l.append(round(ending_shares, 2))
            val_l.append(round(month_end_val, 2))

        # Creating the Table
        self.reinvestment_data = pd.DataFrame({"Date":date_l, "Dividend Value":div_l, "Shares Purchased":shares_l, "Month-End Value":val_l, "Ending Shares":end_l})

        # Cleaning Memory
        del div
        del price
        del td_zero
        del p_arr
        del p_idx
        del d_arr
        del d_idx
        del monthly_data
        del filter
        del date_l
        del div_l
        del shares_l
        del end_l
        del val_l

# -------------------------------------------#

    def get_performance(self, required_ret):
        """
        Calculates the yearly and average yearly rate of return without fund reinvestment of dividends and with fund reinvestment of dividends
        Dataframe Columns:
            Year - year 
            R-NR - Rate of Return investing dividends in required return
            AR-NR - Running Geometric average rate of return investing dividends in required return
            R-R - Rate of Return reinvesting dividends
            AR-R - Running Geometric average rate of return reinvesting dividends
        """

        # Initializing Lists for Performance DataFrame
        year_l = list()
        rnr_l = list()
        rnrval_l = list()
        arnr_l = list()
        rnr_cost_basis_l = list()
        rr_l = list()
        rrval_l = list()
        ar_l = list()
        rr_cost_basis_l = list()

        # Getting Year Data
        filter = self.prices.apply(lambda x: x.name.year >= self.start_date.year, axis=1)
        year_l = sorted(list(set([x.year for x in self.prices.loc[filter].index])))

        # Popping current year
        year_l = year_l[:-1]

        # Getting Rate of Return assuming reinvestment in required return
        div = copy.deepcopy(self.dividends)
        div.reset_index(inplace=True)
        monthly_data = copy.deepcopy(self.monthly_data)
        monthly_data.reset_index(inplace=True)

        # Initializing Dividend Fund Pool
        div_total_val = 0

        for year in year_l:
            # Initializing Variables
            div_yr_val = 0
            eoy = dt.strptime(f'{year+1}/01/01', '%Y/%m/%d').replace(tzinfo=div["Date"].iloc[0].tzinfo)

            # Filtering dividends by year
            filter = div.apply(lambda x: (x["Date"].year == year), axis=1)
            div_year = div.loc[filter]

            # Looping through all dividends in the year
            for idx in range(0, len(div_year["Date"])):
                days = (eoy - div_year["Date"].iloc[idx])
                period_ret = days.days / 365
                div_yr_val += (self.start_shares * div["Dividends"].iloc[idx]) * (1 + ((required_ret/100)*period_ret))
            
            # Calculating Rate of Return
            if year_l.index(year) == 0:
                p_0 = self.prices.loc[self.start_date]["Close"]*self.start_shares
            else:
                filter = monthly_data.apply(lambda x: (x["Date"].year == year-1 ) & (x["Date"].month == 12), axis=1)
                p_0 = (monthly_data.loc[filter]["Close"].iloc[0])*self.start_shares
            
            filter = monthly_data.apply(lambda x: (x["Date"].year == year ) & (x["Date"].month == 12), axis=1)
            p_1 = (monthly_data.loc[filter]["Close"].iloc[0])*self.start_shares

            div_pool_ret = div_total_val*(required_ret/100)
            div_pool_w = (div_total_val) / (div_total_val + p_0)
            total_ret = ((1-div_pool_w)*((p_1 - p_0 + div_yr_val) / p_0)) + (div_pool_w*(required_ret/100))
            val_prop = 1 + total_ret

            # Appending to Lists
            rnr_cost_basis_l.append(p_0 + div_total_val)
            rnr_l.append(total_ret*100)
            rnrval_l.append(val_prop)
            arnr_l.append(geometric_mean(rnrval_l) - 1)

            # Adjusting Dividend Pool
            div_total_val += div_pool_ret + div_yr_val

        # Getting Rate of Return Assuming Reinvestment in Fund

        for year in year_l:

             # Calculating Rate of Return
            if year_l.index(year) == 0:
                p_0 = self.start_val
            else:
                filter = self.reinvestment_data.apply(lambda x: (x["Date"].year == year-1 ) & (x["Date"].month == 12), axis=1)
                p_0 = self.reinvestment_data.loc[filter]["Month-End Value"].iloc[0]

            filter = self.reinvestment_data.apply(lambda x: (x["Date"].year == year ) & (x["Date"].month == 12), axis=1)
            p_1 = self.reinvestment_data.loc[filter]["Month-End Value"].iloc[0]

            total_ret = ((p_1 - p_0) / p_0)
            val_prop = 1 + total_ret

            # Appending to Lists
            rr_cost_basis_l.append(p_0)
            rr_l.append(total_ret*100)
            rrval_l.append(val_prop)
            
            ar_l.append(geometric_mean(rrval_l) - 1)     

        # Creating Dataframe
        self.investment_performance = pd.DataFrame({"Year":year_l,
                                                     "Cost Basis w/ Reinvestment":rr_cost_basis_l,
                                                     "Rate w/ Reinvestment":rr_l,
                                                     "Geometric Return w/ Reinvestment":ar_l,
                                                     "Cost Basis w/ Required Return": rnr_cost_basis_l,
                                                     "Rate w/ Required Return":rnr_l,
                                                     "Geometric Return w/ Required Return":arnr_l}) 
        
        # Cleaning Memory
        del div
        del div_total_val
        del monthly_data
        del p_0
        del p_1
        del filter
        del year_l
        del rnr_l
        del rnrval_l
        del arnr_l
        del rnr_cost_basis_l
        del rr_l
        del rrval_l
        del ar_l
        del rr_cost_basis_l

