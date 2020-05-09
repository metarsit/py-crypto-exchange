import hashlib
import requests
import time
import re
import urllib

from enum import Enum

API_URL = "https://api.crypto.com"
TIMEOUT = 1000


class MarketAPI:
    def __http_get(self, url, param={}):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = urllib.parse.urlencode(param)
        try:
            response = requests.get(url, data, headers=headers, timeout=TIMEOUT)
            return response.json()
        except Exception as e:
            return {"code": "-1", "msg": e}

    def symbols(self):
        """ List all available market symbols
        """
        url = API_URL + "/v1/symbols"
        return self.__http_get(url=url)

    def ticker(self, symbol=None):
        """ Get tickers in one/all available markets
        """
        url = API_URL + "/v1/ticker"
        return self.__http_get(url=url, param={"symbol": symbol} if symbol else {})

    def ticker_price(self):
        """ Get latest execution price for all markets
        """
        url = API_URL + "/v1/ticker/price"
        return self.__http_get(url=url)

    def klines(self, symbol, period=1):
        """ Get k-line data over a specified period
        """
        allowed_periods = [1, 5, 15, 30, 60, 1440, 10080, 43200]
        if period not in allowed_periods:
            raise ValueError("Period selected is not in allowed period")
        url = API_URL + "/v1/klines"
        return self.__http_get(url=url, param={"symbol": symbol, "period": period})

    def trades(self, symbol):
        """ Get last 200 trades in a specified market
        """
        url = API_URL + "/v1/trades"
        return self.__http_get(url=url, param={"symbol": symbol})

    def depth(self, symbol, step="step0"):
        """ Get last 200 trades in a specified market
        """
        allowed_steps = ["step0", "step1", "step2"]
        if step not in allowed_steps:
            raise ValueError("Type selected is not in allowed type")
        url = API_URL + "/v1/depth"
        return self.__http_get(url=url, param={"symbol": symbol, "type": step})


class UserAPI:
    def __init__(self, api_key, secret_key):
        self.__api_key = api_key
        self.__secret_key = secret_key

    def __user_signature(self, param={}):
        epoch_milli = "%d" % int(round(time.time() * 1000))
        sorted_params = sorted(param.items(), key=lambda d: d[0], reverse=False)

        # A joint string is required to be in this format
        joint_string = (
            "api_key"
            + self.__api_key
            + "".join(map(lambda x: str(x[0]) + str(x[1] or ""), sorted_params))
            + "time"
            + epoch_milli
            + self.__secret_key
        )
        sign = hashlib.sha256(joint_string.encode("utf-8")).hexdigest()

        param["api_key"] = self.__api_key
        param["time"] = epoch_milli
        param["sign"] = sign

        return param

    def __http_post(self, url, param={}):
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
        }
        data = urllib.parse.urlencode(param)
        try:
            response = requests.post(url, data, headers=headers, timeout=TIMEOUT)
            return response.json()
        except Exception as e:
            return {"code": -1, "msg": e}

    def balance(self):
        """ List all account balance of user
        """
        url = API_URL + "/v1/account"
        param = self.__user_signature()
        return self.__http_post(url=url, param=param)

    def show_order(self, symbol, order_id):
        """ Get order detail
        """
        url = API_URL + "/v1/showOrder"
        param = {}
        param["symbol"] = symbol
        param["order_id"] = order_id
        return self.__http_post(url=url, param=self.__user_signature(param))

    def cancel_all_oder(self, symbol):
        """ Cancel all orders in a particular market
        """
        url = API_URL + "/v1/cancelAllOrders"
        param = {}
        param["symbol"] = symbol
        return self.__http_post(url=url, param=self.__user_signature(param))

    def cancel_order(self, symbol, order_id):
        """ Cancel an order
        """
        url = API_URL + "/v1/orders/cancel"
        param = {}
        param["symbol"] = symbol
        param["order_id"] = order_id
        return self.__http_post(url=url, param=self.__user_signature(param))

    def get_all_orders(self, symbol):
        """ List all orders in a particular market
        """
        url = API_URL + "/v1/allOrders"
        param = {}
        param["symbol"] = symbol
        return self.__http_post(url=url, param=self.__user_signature(param))

    def get_trades(
        self, symbol, start_date=None, end_date=None, page=None, page_size=None
    ):
        """ List all executed orders
        """
        url = API_URL + "/v1/myTrades"
        pattern = "[0-9]{4}-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]"
        param = {}
        param["symbol"] = symbol

        if start_date is not None:
            if not re.match(pattern, start_date):
                raise ValueError("Start Date Pattern mismatch")
            param["startDate"] = start_date
        if end_date is not None:
            if not re.match(pattern, end_date):
                raise ValueError("End Date Pattern mismatch")
            param["endDate"] = end_date
        if page is not None:
            param["page"] = page
        if page_size is not None:
            param["pageSize"] = page_size

        return self.__http_post(url=url, param=self.__user_signature(param))

    def open_orders(self, symbol, page=None, page_size=None):
        """ List all open orders in a particular market
        """
        url = API_URL + "/v1/openOrders"
        param = {}
        param["symbol"] = symbol

        if page is not None:
            param["page"] = page
        if page_size is not None:
            param["pageSize"] = page_size

        return self.__http_post(url=url, param=self.__user_signature(param))
