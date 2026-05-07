"""Nifty50 seed list — sourced from docs/nifty50-stocks.md.

Note: file lists 30 tickers (MVP scope), naming retained for consistency with the
business label "Nifty50". Industry is filled at seed time via yfinance .info.
"""

NIFTY_50: list[str] = [
    "RELIANCE.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "ICICIBANK.NS", "TCS.NS",
    "BAJFINANCE.NS", "LT.NS", "HINDUNILVR.NS", "INFY.NS", "SUNPHARMA.NS", "MARUTI.NS",
    "ADANIPORTS.NS", "AXISBANK.NS", "ITC.NS", "TITAN.NS", "KOTAKBANK.NS", "ONGC.NS",
    "ULTRACEMCO.NS", "ADANIENT.NS", "HCLTECH.NS", "BEL.NS", "JSWSTEEL.NS", "POWERGRID.NS",
    "COALINDIA.NS", "BAJAJ-AUTO.NS", "BAJAJFINSV.NS", "NESTLEIND.NS", "TATASTEEL.NS",
    "ASIANPAINT.NS",
]

COMPANY_NAMES: dict[str, str] = {
    "RELIANCE.NS": "Reliance Industries",
    "HDFCBANK.NS": "HDFC Bank",
    "BHARTIARTL.NS": "Bharti Airtel",
    "SBIN.NS": "State Bank of India",
    "ICICIBANK.NS": "ICICI Bank",
    "TCS.NS": "Tata Consultancy Services",
    "BAJFINANCE.NS": "Bajaj Finance",
    "LT.NS": "Larsen & Toubro",
    "HINDUNILVR.NS": "Hindustan Unilever",
    "INFY.NS": "Infosys",
    "SUNPHARMA.NS": "Sun Pharmaceutical",
    "MARUTI.NS": "Maruti Suzuki",
    "ADANIPORTS.NS": "Adani Ports",
    "AXISBANK.NS": "Axis Bank",
    "ITC.NS": "ITC",
    "TITAN.NS": "Titan",
    "KOTAKBANK.NS": "Kotak Mahindra Bank",
    "ONGC.NS": "ONGC",
    "ULTRACEMCO.NS": "UltraTech Cement",
    "ADANIENT.NS": "Adani Enterprises",
    "HCLTECH.NS": "HCL Technologies",
    "BEL.NS": "Bharat Electronics",
    "JSWSTEEL.NS": "JSW Steel",
    "POWERGRID.NS": "Power Grid",
    "COALINDIA.NS": "Coal India",
    "BAJAJ-AUTO.NS": "Bajaj Auto",
    "BAJAJFINSV.NS": "Bajaj Finserv",
    "NESTLEIND.NS": "Nestle India",
    "TATASTEEL.NS": "Tata Steel",
    "ASIANPAINT.NS": "Asian Paints",
}
