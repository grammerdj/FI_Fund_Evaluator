# FI_Fund_Evaluator
This is a quick program I developed for my Dad that takes a list of fund tickers along with some configuration about investment start dates, starting capital, and required return as an input as outputs fund performance metrics.

Configuration:

  The following things can be configured through the config.json document:
1. Input Location
2. Output Location
3. Logger Location
4. Input file name config
5. Output file name config
6. Logger file name config
7. Staring Capital
8. Start Date
9. Required Return

YOU WILL HAVE TO EDIT THE LOCATION OF THE CONFIG DOCUMENT WITHIN THE SCRIPT TO USE. IT APPEARS IN config.py AND fund_returns.py

How to Use:

1. Enter the list of tickers in the input excel file under the columns 'Tickers'.
2. Edit necessary configuration
3. Run the program

Output:

  The script will output an excel document for each of the tickers given in the input. It has three sheets. The first one gives monthly data for price and dividends. The second one gives reinvestment metrics using the start date and starting capital. The last one calculates rates of return with reinvestment and required return, so you can compare. If you need more information about the assumptions made in the script, please check the comments within the script.

Thank you!
