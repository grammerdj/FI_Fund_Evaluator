# FI_Fund_Evaluator
This is a program I developed for my Dad that takes a list of fund tickers along with some configuration about investment start dates, starting capital, and required returns/volatility as an input and outputs fund performance metrics and optimized portfolios.

Dependencies:
1. PyPortfolioOpt REQUIRES C++ TO RUN!


Configuration:

  The following things can be configured through the config.json document:
1. Input Location
2. Output Location
3. Summary Files Location
4. Input file name config
5. Output file name config
6. Summary file name config
7. Staring Capital
8. Start Date
9. Required Return
10. Risk-free Rate
11. Minimum Return for Variance Optimizer
12. Minimum Volatility for Return Optimizwe

YOU WILL HAVE TO EDIT THE LOCATION OF THE CONFIGATION AND LOGGING DOCUMENTS WITHIN THE SCRIPT TO USE. IT APPEARS IN config.py (line 19) AND fund_returns.py (line 27)

How to Use:

1. Enter the list of tickers in the input excel file under the columns 'Tickers'.
2. Edit necessary configuration
3. Run the program

Output:

1. The script will output an excel document for each of the tickers given in the input. It has three sheets. The first one gives monthly data for price and dividends. The second one gives reinvestment metrics using the start date and starting capital. The last one calculates rates of return with reinvestment and required return, so you can compare.

2. This script also outputs a summary document with three sheets. The first sheet contains a summary of the risk and return metrics for each fund run through the program. The second sheet contains the tickers of all funds in the script that have existed for less than 1 full calendar year, and therefore were dropped from the optimization problem. The last sheet contains the risk and return specs for a Max-Sharpe portfolio of your funds optimal minimum return and minimum volatility portfolios. The weights for these portfolios are saved separately in the summary file location.
  
3. If you need more information about the assumptions made in the script, please check the comments within the script.

Thank you!
