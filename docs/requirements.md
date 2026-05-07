\# Project Overview

This is a web application which can run across all devices (desktop,
laptop, tablets and mobile). The application will be used to fetch stock
prices, do advanced analysis to extract key insights with regards to
stock performance and scrape the news to find relevant headlines about
the respective companies.

\# Key features of Application

- Sign in page: user will sign in using user id and password. New users
  will have to register first and then will sign in to proceed further.

- Dashboard: this page will show the most recent analysis of stocks.
  There are other clickable buttons on this page.

  - Nifty50: when user clicks on this button, Nifty50 page opens.

  - Refresh: when user clicks on this button, analysis data refreshes.

\# Workflow

- User will land on login page. If user hasn't registered then user will
  register himself. After successful registration, sign in page will
  automatically appear.

- User will sign in. After successful sign in, dashboard page will
  appear.

- From this page, user can perform any of the following actions.

  - click Nifty50: Nifty50 page opens.

  - click Refresh: application will fetch stock price from Yahoo Finance
    (<https://finance.yahoo.com/quote/%5ENSEI/>) and will run analysis.
    Latest analysis will be shown on UI.

  - click Stock Name: stock page will open

- Home page will show the latest analysis.

\# Business Rules

- Register Page

  - Mandatory Fields: User name, User Id, Password, Re-enter Password.

  - Values in Password and Re-enter Password should match.

  - Message:

    - if registration is successful then show message "Registration
      successful"

    - if registration failed then show message: Registration failed,
      Retry"

  - If registration is successful then sign in page opens automatically.

- Sign in Page

  - If sign in is successful then show message "sign in successful".
    Dashboard page opens automatically.

  - If sign in fails then show message "user id or password invalid.
    Retry"

  - If user clicks Register then open Registration page.

- Dashboard Page

  - Be default, analysis table will be generated on last 02 Year of
    stock data.

  - Columns in Analysis Table

    - Stock Name

    - Industry: industry of the stock

    - Last Price

    - High

    - Low

    - Median: Median price of stock for the duration for which analysis
      is performed

  - Select the timeline (1M 3M 6M 9M 1Y 1.5Y 2Y): analysis will be shown
    for that timeframe. For ex: user selects 6M. Analysis will be
    performed on last 6 months data. Accordingly, the analysis table
    will update.

  - Search bar: user can search a stock listed in NIFTY50 by entering
    either \<stock name\> or \<stock id\>. System will search the
    information in database. If current data is not available then it
    will fetch from Yahoo Finance.

  - Click Refresh:

    - application will fetch stock price from Yahoo Finance
      (<https://finance.yahoo.com/quote/%5ENSEI/>).

      - If stock id and fetch date is blank then fetch data for a year.

      - Else it will fetch only the incremental data since the fetch
        date to current date. For ex: current date is 10^th^ May 2025.
        Last date when data was fetched was 20^th^ Apr 2025. System will
        fetch date from 21^st^ Apr 2025 to 10^th^ May 2025.

      - If fetch date of a stock is current date, then do not fetch
        data. Check for next stock.

      - As soon as data for a stock is fetched successfully, save the
        data in database along with fetch date. If data fetch fails,
        whatever data has been fetched successfully till the failure is
        saved in database. Do not abort the whole process.

    - Prepare Analysis Table

    - Show the Analysis Table on UI.

    - Fetch headline news about the stock / company.

      - Use Google News RSS (free allowed) filtered by company name, and
        link out to the source. Use NewsAPI.org free tier (100 req/day).

      - Store the headline news along with url and date in database.

      - Fetch headline news if the last fetch_date_news is older than 30
        days. For ex: if the news was fetched 20 days back then do not
        fetch the news.

  - If overall slope of price change is Positive during the timeline AND
    stock price at the end is greater than price at start of timeline by
    more than 5% then label "Strong Upward" ![Bar graph with upward
    trend](media/image2.svg){width="0.20586832895888013in"
    height="0.20586832895888013in"}

  - If overall slope of price change is Flat during the timeline AND
    stock price at the end is greater than price at start of timeline by
    \<3% then label "Weak Upward" ![Upward
    trend](media/image4.svg){width="0.2305161854768154in"
    height="0.2305161854768154in"}.

  - If overall slope of price change is Negative during the timeline AND
    stock price at the end is lower than price at start of timeline by
    more than 5% then label "Strong Downward"![Bar graph with downward
    trend](media/image6.svg){width="0.19693897637795277in"
    height="0.19693897637795277in"}

  - If overall slope of price change is Negative during the timeline AND
    stock price at the end is lower than price at start of timeline by
    less than 3% then label "Weak Downward" ![Downward
    trend](media/image8.svg){width="0.2424245406824147in"
    height="0.2424245406824147in"}

  - Rest of the cases, label as "Neutral" ![Line arrow
    Straight](media/image10.svg){width="0.1736111111111111in"
    height="0.1736111111111111in"}

- Stock Page

  - User will click a \<Stock Name\> on dashboard page to come to this
    page. This page will show detailed analysis of the stock.

  - Price chart over timeline is shown. For the timeline

    - 1M: daily price for 1 month is shown

    - 3M: weekly price for 3 months is shown. Average of Daily price is
      aggregated as Weekly price

    - 6M: weekly price for 3 months is shown. Average of Daily price is
      aggregated as Weekly price

    - 9M: monthly price for 9 months is shown. Average of Daily price is
      aggregated as Monthly price

    - 1Y: monthly price for 1 Year is shown. Average of Daily price is
      aggregated as Monthly price

    - 1.5Y: monthly price for 1.5 Year is shown. Average of Daily price
      is aggregated as Monthly price

    - 2Y: monthly price for 2 Year is shown. Average of Daily price is
      aggregated as Monthly price

  - Headlines: retrieve headline news from database and show on UI

- Nifty50

  - If last fetch date is blank then fetch data for a Year from Yahoo
    Finance (<https://finance.yahoo.com/quote/%5ENSEI/>).

  - If last fetch date is not blank and less than current date then
    fetch incremental Nifty50 data since the last fetch date.

  - Shows Nifty50 price movement over a timeline

  - If last fetch date is same as current date, then do not fetch data

\# Database

- Registration details are saved in database.

- Stock data will be saved in database along with last fetch date.

- NIFTY50 data will be saved along with last fetch date.

- Headlines text will be stored along with url.

\# User Message

- Always show the message on screen whether task has successfully
  completed or failed or is in progress. It helps user to better engage
  with system.

\# Error handling:

- Handle error gracefully.

- if API call fails then abort the process and show message to user to
  retry.

- if data fetch fails completely then show message to user to retry.

- if news scraping fails then continue. Show the analysis without news
  on screen.

I am building this product as a MVP to test few basic ideas. Therefore,
I want to keep the technology stack very simple, easy to maintain and
open source or free one. I want to deploy the application on internet
and test among a small group with very small data. I would like the
application to be stable and robust.

Read the requirements carefully to fully understand about the
application. If you need additional information to understand the
requirements better then ask questions.
