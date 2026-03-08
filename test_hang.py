import os
import requests

old_request = requests.Session.request
def new_request(self, *args, **kwargs):
    self.trust_env = False
    return old_request(self, *args, **kwargs)
requests.Session.request = new_request

import time
import akshare as ak

funcs = [
    ("ak.stock_individual_info_em(symbol='600519')", lambda: len(ak.stock_individual_info_em(symbol="600519"))),
    ("ak.stock_financial_analysis_indicator(symbol='600519')", lambda: len(ak.stock_financial_analysis_indicator(symbol="600519"))),
    ("ak.stock_zh_a_spot_em()", lambda: len(ak.stock_zh_a_spot_em())),
    ("ak.macro_china_cpi_yearly()", lambda: len(ak.macro_china_cpi_yearly())),
    ("ak.macro_china_gdp_yearly()", lambda: len(ak.macro_china_gdp_yearly())),
    ("ak.rate_interbank()", lambda: len(ak.rate_interbank())),
    ("ak.js_news(indicator='财经日历')", lambda: len(ak.js_news(indicator="财经日历"))),
]

for name, func in funcs:
    print(f"Testing {name}...")
    t0 = time.time()
    try:
        res = func()
        print(f"  Done in {time.time()-t0:.2f}s, length: {res}")
    except Exception as e:
        print(f"  Failed in {time.time()-t0:.2f}s: {e}")



