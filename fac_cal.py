# Factor Function
#
import pandas as pd
import numpy as np
from pandas import DataFrame as df
from datetime import date, datetime, timedelta
from rqdatac import *
#===============================================================================================================================#
class Factor_Part_1:
    def get_1month_basic_data(self):
        self.__BasicDataCode = ['fundamentals.income_statement.operating_revenue',
                              'fundamentals.income_statement.net_profit',
                              'fundamentals.income_statement.profit_from_operation',
                              'fundamentals.cash_flow_statement.cash_from_operating_activities',
                              'fundamentals.financial_indicator.inc_gross_profit',
                              'fundamentals.financial_indicator.inc_operating_revenue',
                              'fundamentals.financial_indicator.inc_net_profit',
                              'fundamentals.financial_indicator.return_on_equity',
                              'fundamentals.income_statement_TTM.operating_profitTTM',
                              'fundamentals.income_statement_TTM.operating_revenueTTM',
                              'fundamentals.income_statement_TTM.net_profitTTM',
                              'fundamentals.cash_flow_statement_TTM.net_operate_cashflowTTM'
                              'fundamentals.market_cap'
                              'fundamentals.trading_volume'
                             ]
        self.__q = eval('query(%s).filter(fundamentals.income_statement.stockcode.in_(self.StockPool))'%','.join(self.__BasicDataCode))
        self.BasicData = get_fundamentals(self.__q, self.DATE, '9q').sort_index(1).sort_index(2)

        for item in ['.'.join(self.__BasicDataCode).split('.')[i] for i in [2, 5, 8, 11]]:
            s = int((self.BasicData[item].index[0].date().month + 2) / 3)
            if s == 1:
                Slist = [1, 2, 3, 5, 6, 7]
            elif s == 2:
                Slist = [1, 2, 4, 5, 6, 8]
            elif s == 3:
                Slist = [1, 3, 4, 5, 7, 8]
            elif s == 4:
                Slist = [2, 3, 4, 6, 7, 8]
            for i in Slist:
                self.BasicData[item].iloc[i] -= self.BasicData[item].iloc[i-1]
        self.BasicData = self.BasicData.fillna(method='ffill').fillna(0)
    def momentum(self):
        data = self.BasicData['market_cap'].T
        self.StockData['momentum'] = np.array((data[data.columns[-1]] - data.mean(1)) / data.std(1)).tolist()
    def volume(self):
        data = self.BasicData['trading_volume'].T
        self.StockData['volume'] = np.array((data[data.columns[-1]] - data.mean(1)) / data.std(1)).tolist()
