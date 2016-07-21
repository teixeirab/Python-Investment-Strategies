The Contrarian Algo

An application that connected to a TWS trading account trades on equity investments that have fallen by more than 15%
as of last trading day.

Investment Strategy

It has been shown several times by academics and practitioners that investors tend to overreact in the short run to
negative news. In order to take advantage of this psychological effect one could create a portfolio of stocks that have
fallen more than 15% within a given day. While a lot of these stocks may have fallen in price due to correct pricing
changes, the algorithm takes advantage of the notion that winners will more often than not make up for looser. I would
also highly recommend adding more "quality" filters to the investment strategy (ie. ROE, ROIC, leverage, probability of
default PS: did not include in this version since that reliable fundamental data is not available for free)

If you want to run on your machine

- Clone to your machine
- Install all pythons packages used in the program
- Create a free account with Quandl and input your API id in the url request
- (Create a Interactive Brokers account) Add your TWS account information
- Download MySQL and make sure to include your connection info whenever the app opens a SQL connection
- Make sure to play with paper trading before you deploy the algorithm in your real trading accont
- Create a task scheduler to run the application every weekday at 9:00am
- Optional: Add quality filters to the investment strategy
- Enjoy the run



