from finviz.screener import Screener
import json
import requests
from bs4 import BeautifulSoup

def getScreenerInfo(filters):
    stocks = []
    url = "https://finviz.com/screener.ashx?v=111&f=an_recom_buybetter,cap_smallunder,exch_nasd,fa_curratio_o2,fa_epsyoy1_o10,fa_quickratio_o2,sh_avgvol_o100,sh_curvol_o100,sh_float_u50,sh_price_u5,sh_short_u5&o=-epsyoy1"

    some_filters = [
                        filters['Exchange']['NASDAQ'],                    
                        filters['Market Cap.']['-Small (under $2bln)'],
                        filters['Average Volume']['Over 100K'],
                        filters['Float Short']['Under 5%'],
                        filters['Analyst Recom.']['Buy or better'],
                        filters['Current Volume']['Over 100K'],
                        filters['Price']['Under $7'],
                        filters['Current Ratio']['Over 2'],
                        filters['EPS growthnext year']['Over 10%'],
                        # filters["Quick Ratio"]["Over 2"],
                        filters["Float"]["Under 100M"]
                    ]
    stocks = Screener(filters=some_filters, order='-epsyoy1')
    # stocks = Screener.init_from_url(url)

    return stocks

def getRedditMentions(period, subreddits):
    tickers = {}
    
    for subreddit in subreddits:
        try:
            res = requests.get(url = f"http://unbiastock.com/TableReddit.php?compare2={subreddit}&compare_sector={period}")
        except requests.exceptions.RequestException as e:
            print("request error")
            continue
        
        if res.status_code != 200 and res.status_code != 201:
            continue
        
        html = BeautifulSoup(res.text, features="lxml")
        
        rows = html.table.tbody.find_all('tr')
        
        for row in rows:
            data = row.find_all('th')
            data = [ele.text.strip() for ele in data]
            if data[0] not in tickers:
                tickers[data[0]] = {
                        "Score": data[1],
                        f"Last {period//2}H score": data[2],
                        f"{period//2}H-{period}H Score": data[3],
                        "Score change": data[4],
                        "%Change in volume": data[9]
                    }
    
    return tickers

if __name__ == '__main__':
    common = []
    screenerStocks = []
    redditTickers = {}

    with open("filters.json") as file:
        filters = json.load(file)
        screenerStocks = getScreenerInfo(filters)
        # print(screenerStocks)
        # screenerStocks.to_csv()
    
    period = 24
    subreddits = ["pennystocks", "RobinHoodPennyStocks"]
    redditTickers = getRedditMentions(period, subreddits)

    for stock in screenerStocks.data:
        if stock["Ticker"] in redditTickers:
            common.append({**redditTickers[stock["Ticker"]], **stock})


    print("{:<7} | {:<5} | {:<5} | {:<15} | {:<5} | {:<8} | {:<15} | {:<20} | {:<15} | {:<15} | {:<10} | {:<5}".format("Ticker", "No.", "Score", "Score change", 
                                                                                                                        "Price", "Change", "Volume", "%Change in volume",
                                                                                                                        f"Last {period//2}H score", 
                                                                                                                        f"{period//2}H-{period}H Score", "Market Cap", "P/E"
                                                                                                                        ))

    for s in common:
            print("{:<7} | {:<5} | {:<5} | {:<15} | {:<5} | {:<8} | {:<15} | {:<20} | {:<15} | {:<15} | {:<10} | {:<5}".format(s['Ticker'], s["No."], s['Score'], s["Score change"],
                                                                                                                                s["Price"], s["Change"], s["Volume"], 
                                                                                                                                s["%Change in volume"], s[f"Last {period//2}H score"],
                                                                                                                                s[f"{period//2}H-{period}H Score"], s["Market Cap"], s["P/E"],
                                                                                                                                ))
