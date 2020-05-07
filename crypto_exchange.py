import hashlib
import requests
import time
import urllib

API_URL = "https://api.crypto.com"
TIMEOUT = 1000

def get_timestamp():
    ts = "%d"%int(round(time.time() * 1000))
    return ts

class MarketAPI:
    def __http_get(self, url, params={}):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = urllib.parse.urlencode(params)
        try:
            response = requests.get(url, data, headers=headers, timeout=TIMEOUT)
            return response.json()
        except Exception as e:
            return {"code": '-1', "msg": e}

    def symbols(self):
        ''' List all available market symbols
        '''
        url = API_URL + "/v1/symbols"
        return self.__http_get(url=url)

    def ticker(self, sym=None):
        ''' Get tickers in one/all available markets
        '''

        url = API_URL + "/v1/ticker"
        return self.__http_get(url=url, params={"symbol": sym} if sym else {})

    def ticker_price(self):
        ''' Get latest execution price for all markets
        '''
        url = API_URL + "/v1/ticker/price"
        return self.__http_get(url=url)

    def klines(self, sym, period=1):
        ''' Get k-line data over a specified period
        '''
        allowed_periods = [1, 5, 15, 30, 60, 1440, 10080, 43200]
        if period not in allowed_periods:
            raise ValueError("Period selected is not in allowed period")
        url = API_URL + "/v1/klines"
        return self.__http_get(url=url, params={"symbol": sym, "period": period})

    def trades(self, sym):
        ''' Get last 200 trades in a specified market
        '''
        url = API_URL + "/v1/trades"
        return self.__http_get(url=url, params={"symbol": sym})

    def depth(self, sym, step="step0"):
        ''' Get last 200 trades in a specified market
        '''
        allowed_steps = ["step0", "step1", "step2"]
        if step not in allowed_steps:
            raise ValueError("Type selected is not in allowed type")
        url = API_URL + "/v1/depth"
        return self.__http_get(url=url, params={"symbol": sym, "type": step})
