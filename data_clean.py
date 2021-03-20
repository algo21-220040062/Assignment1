import pandas as pd
import numpy as np
from pandas import DataFrame as df
from datetime import date, datetime, timedelta
from rqdatac import *
from allen.FactorFunction import Factor_Part_1, Factor_Part_2, Factor_Part_3, Factor_Part_4, Factor_Part_5, Factor_Part_6

class FactorCal(Factor_Part_1, Factor_Part_2, Factor_Part_3, Factor_Part_4, Factor_Part_5, Factor_Part_6):
    def __init__(self):
        self.DATE = ''
        self.q_date = ''
        self.__data = ''
        self.__BasicDataCode = ''
        self.BasicData = ''
        self.BasicData_q = ''
        self.StockData = ''
        self.StockPool = ''
        self.__q = ''
        self._flist = ''
        self.FactorList = []
        self.__test = ''

    def __add__(self, other):
        if self.DATE == '':
            return other
        elif other.DATE == '':
            return self
        else:
            if isinstance(self.DATE, list):
                if isinstance(other.DATE, list):
                    f = FactorCal()
                    f.StockData = pd.concat([self.StockData, other.StockData]).reset_index(drop=True)
                    f.FactorList = self.FactorList
                    f.DATE = self.DATE + other.DATE
                    f.q_date = self.q_date + other.q_date
                    f.StockPool = {**self.StockPool, **other.StockPool}
                    return f
                else:
                    other.StockPool = {other.DATE : other.StockPool}
                    other.DATE = [other.DATE]
                    other.q_date = [other.q_date]
                    return self.__add__(other)
            else:
                self.StockPool = {self.DATE : self.StockPool}
                self.DATE = [self.DATE]
                self.q_date = [self.q_date]
                return self.__add__(other)

    def __get_all_stock(self):
        def str_datetime(s):
            if s == '0000-00-00':
                return date(2020,1,1)
            else:
                return datetime.strptime(s, '%Y-%m-%d').date()            
        self.__data = all_instruments('CS')
        self.__data['listed_date'] = self.__data['listed_date'].apply(str_datetime)
        self.__data['de_listed_date'] = self.__data['de_listed_date'].apply(str_datetime)

    def __s_trade_date(self, year, season):
        D = date(year + ((season - 1) // 4), (((season - 1)% 4) + 1)* 3 - 2, 1)
        D = get_trading_dates(D, D + timedelta(days=10))[0]
        return D

    def __m_trade_date(self, year, month):
        D = date(year + ((month - 1) // 12), ((month - 1)% 12) + 1, 1)
        D = get_trading_dates(D, D + timedelta(days=10))[0]
        return D

    def set_date(self, y, s, t):
        if t == 0:
            self.DATE = self.__s_trade_date(y, s)
            self.q_date = self.__s_trade_date(y, s + 1)
        elif t == 1:
            self.DATE = self.__m_trade_date(y, s)
            self.q_date = self.__m_trade_date(y, s + 1)

    def __get_stock_pool(self):
        if self.DATE == '':            
            EX = 'Please set date:\nWhich kind of date you wanna get?\n0 : season\n1 : month'
            print(EX)
            T = eval(input('Please input 0/1:'))
            while T not in [0, 1]:
                T = eval(input('Please input 0 or 1:'))
            y = eval(input('Year:'))
            while y not in range(2006, 2019):
                y = eval(input('Please input correct year (from 2006 to 2018):'))
            if T == 0:
                q = eval(input('Season:'))
                while q not in range(1, 5):
                    q = eval(input('Please input correct season (from 1 to 4):'))
            elif T == 1:
                q = eval(input('Month:'))
                while q not in range(1, 13):
                    q = eval(input('Please input correct month (from 1 to 12):'))
            self.set_date(y, q, T)
            self.__get_stock_pool()
        else:
            self.__get_all_stock()
            self.StockData = self.__data.loc[self.__data['de_listed_date'] > self.DATE].loc[self.__data['listed_date'] + timedelta(days=1200) < self.DATE].loc[self.__data['special_type'] != 'ST'].loc[self.__data['special_type'] != 'StarST'].loc[self.__data['special_type'] != 'PT'][['order_book_id', 'sector_code']].copy()
            self.StockPool = np.array(self.StockData['order_book_id']).tolist()
            #pool = np.array(self.StockData['order_book_id']).tolist()
            #pool_1 = is_suspended(pool, self.DATE, self.DATE).T
            #pool_2 = is_suspended(pool, self.q_date, self.q_date).T
            #pool_3 = is_st_stock(pool, self.DATE, self.DATE).T
            #pool_1 = pool_1.loc[pool_1[self.DATE]].index.tolist()
            #pool_2 = pool_2.loc[pool_2[self.q_date]].index.tolist()
            #pool_3 = pool_3.loc[pool_3[self.DATE]].index.tolist()
            #self.StockPool = list(set(pool).difference(set(pool_1).union(set(pool_2)).union(set(pool_3))))
            self.StockPool.sort()
            self.StockData = self.StockData[self.StockData['order_book_id'].isin(self.StockPool)]
            self.StockData['total_shares'] = np.array(get_shares(self.StockPool, self.DATE - timedelta(days=10), self.DATE, 'total').iloc[-1]).tolist()
            self.StockData['circulation_shares'] = np.array(get_shares(self.StockPool, self.DATE - timedelta(days=10), self.DATE, 'circulation_a').iloc[-1]).tolist()
            self.StockData['last_y_shares'] = np.array(get_shares(self.StockPool, self.DATE - timedelta(days=375), self.DATE - timedelta(days=365), 'total').iloc[-1]).tolist()

    def __return_cal(self):
        data = get_price(self.StockPool, self.q_date, self.q_date, '1d', 'close').sort_index(1)
        p_data = get_price(self.StockPool, self.DATE, self.DATE, '1d', 'close').sort_index(1)
        self.StockData['return'] = (np.array(data) / np.array(p_data) - 1)[0]
        self.StockData['Y_1'] = self.StockData['return'].apply(lambda x : [0, 1][x > 0])
        self.StockData['Y_2'] = self.StockData['return'].apply(lambda x : [[0, 1][x >= 0.09], -1][x <= -0.09])

    def strange(self):
        sigma = 3.14826
        data = self.StockData[self.FactorList].copy()
        f_median = data.median()
        f_mad = (data - f_median).apply(np.abs).median()
        high = f_median + 3 * sigma * f_mad
        low = f_median - 3 * sigma * f_mad
        high_data = data - high
        low_data = data - low
        for s in self.FactorList: 
            high_list = [high_data.loc[high_data.loc[:,s]>0].index]
            low_list = [low_data.loc[low_data.loc[:,s]<0].index]
            for i in high_list:
                self.StockData.loc[i, s] = high[s] + np.random.randn(1) / 1000000
            for j in low_list:
                self.StockData.loc[j, s] = low[s] - np.random.randn(1) / 1000000

    def standardize(self):
        data = self.StockData[self.FactorList].copy()
        self.StockData.loc[:,'F1':] = (data - data.mean()) / data.apply(np.std)

    def fac_cal(self):
        print('['+'*'*0+' '*100+']')
        # stock pool
        self.__get_stock_pool()
        print('['+'*'*3+' '*97+']')
        # return
        self.__return_cal()
        print('['+'*'*5+' '*95+']')
        # part 1
        self.get_8season_basic_data()
        self.fac_8season_cal()
        self.FactorList += self._flist
        print('['+'*'*18+' '*82+']')
        # part 2
        self.get_4season_basic_data()
        self.fac_4season_cal()
        self.FactorList += self._flist
        print('['+'*'*31+' '*69+']')
        # part 3
        self.get_2season_basic_data()
        self.fac_2season_cal()        
        self.FactorList += self._flist
        print('['+'*'*44+' '*56+']')
        # part 4
        self.get_1season_basic_data()
        self.fac_1season_cal()        
        self.FactorList += self._flist
        print('['+'*'*57+' '*43+']')
        # part 5
        self.get_yoy_basic_data()
        self.fac_yoy_cal()
        self.FactorList += self._flist
        print('['+'*'*70+' '*30+']')
        # part 6
        self.get_pv_basic_data()
        self.fac_pv_cal()
        self.FactorList += self._flist
        print('['+'*'*83+' '*17+']')
        # set factor list
        self.FactorList.sort()
        self.FactorList = ['F%d'%i for i in self.FactorList]
        # add trade date
        self.StockData['trade_date'] = self.DATE
        print('['+'*'*90+' '*10+']')
        # del useless columns
        self.StockData = self.StockData[['trade_date', 'order_book_id', 'sector_code', 'return', 'Y_1', 'Y_2', 'market_cap'] + self.FactorList]
        # reset index
        self.StockData = self.StockData.reset_index(drop=True)
        # data clean
        self.strange()
        self.standardize()
        print('['+'*'*95+' '*5+']')
        # reset var
        self.__data = ''
        self.__BasicDataCode = ''
        self.BasicData = ''
        self.BasicData_q = ''
        self.__q = ''
        self._flist = ''
        self.__test = ''
        print('['+'*'*100+' '*0+']')