import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from datetime import date, datetime, timedelta
from rqdatac import *

class FactorTest:
    def __init__(self):
        self.Data = ''
        self.DateList = ''
        self.IndustryList = ''
        self.FactorList = ''
        self.Factor = ''
        self.FactorData = ''
        self.ReturnData = ''
        self.TestData = ''
        self.MonotonyData = ''
        self.StockPool = ''
        self.q_DateList = ''
        self.PriceData = ''
        self.GroupReturn = ''
        self.Y = ''
        self.X = ''
        self.Error = ''
        self.Beta = ''
        self.Y_hat = ''
        self.t = ''
        self.ic = ''
        self.len = ''
        self.model = ''
        self.tt = ''

    def set_data(self, data):
        self.Data = data.set_index('trade_date')
        self.IndustryList = self.Data[['sector_code']].groupby('sector_code').count().index.tolist()
        for industry in self.IndustryList:
            self.Data[industry] = (self.Data['sector_code'] == industry).apply(lambda x : [0, 1][x])

    def set_date_list(self, date_list):
        self.DateList = date_list[0]

    def set_q_date_list(self, q_date_list):
        self.q_DateList = q_date_list[0]

    def set_factor_list(self, factor_list):
        self.FactorList = factor_list

    def set_test_data(self):
        self.TestData = pd.DataFrame(np.zeros([len(self.DateList), 3]), index=self.DateList, columns=['t', 'ic', 'beta'])

    def set_return_data(self):
        self.ReturnData = self.Data['return']

    def set_factor_data(self, factor):
        self.Factor = factor
        self.FactorData = self.Data[[self.Factor, 'market_cap'] + self.IndustryList]
        self.MonotonyData = self.Data[['order_book_id', self.Factor, 'sector_code']]

    def cal_t_value(self):
        self.t = self.model.tvalues[self.Factor]

    def cal_ic_value(self):
        self.ic = 1 - 6 * float((((self.X[self.Factor].rank() - self.Y.rank()) ** 2).sum()) / (self.len * (self.len ** 2 - 1)))

    def regression(self):
        self.model = sm.OLS(self.Y, sm.add_constant(self.X)).fit()
        self.Y_hat = self.model.fittedvalues
        self.Beta = self.model.params[self.Factor]
        self.Error = self.Y - self.Y_hat
        self.cal_t_value()
        self.cal_ic_value()

    def factor_regression(self, factor):
        self.set_factor_data(factor)
        self.set_return_data()
        self.set_test_data()
        for date in self.DateList:
            self.Y = self.ReturnData.loc[date].copy()
            self.X = self.FactorData.loc[date].copy()
            self.len = len(self.X)
            self.regression()
            self.TestData['t'][date] = self.t
            self.TestData['ic'][date] = self.ic
            self.TestData['beta'][date] = self.Beta
        self.TestData['t_abs'] = self.TestData['t'].apply(abs)
        self.TestData['ic_abs'] = self.TestData['ic'].apply(abs)

    def group_return_cal(self):
        date_data_list = []
        for date in self.DateList:
            self.StockPool = self.MonotonyData.loc[date]['order_book_id'].tolist()
            self.PriceData = get_price(self.StockPool, start_date=date,
                                       end_date=self.q_DateList[self.DateList.index(date)]-timedelta(days=1),
                                       fields=['close']).sort_index(1)
            data_1 = self.MonotonyData.loc[date][['group_%d' % i for i in range(1,6)]].copy()
            data_2 = self.PriceData.copy().fillna(method='ffill')
            date_data = pd.DataFrame(np.dot(np.array(data_2), (np.array(data_1))),
                                     index=data_2.index, columns=data_1.columns)
            date_data = date_data / date_data.iloc[0]
            if date_data_list != []:
                date_data = date_data * date_data_list[-1].iloc[-1]
            date_data_list.append(date_data)
        self.GroupReturn = pd.concat(date_data_list, axis=0)

    def monotony_group_div(self):
        self.MonotonyData = self.MonotonyData.reset_index(drop=False)
        date_data_list = []
        for date in self.DateList:
            industry_data_list = []
            for industry in self.IndustryList:
                group_data = self.MonotonyData
                group_data = group_data.loc[group_data['trade_date'] == date]
                group_data = group_data.loc[group_data['sector_code'] == industry]
                group_data = group_data[[self.Factor]].rank().sub(1).floordiv(round(len(group_data) / 5)).add(1).sort_index()
                group_data_list = []
                for i in range(1, 5):
                    group_data_list.append(group_data[self.Factor].apply(lambda x : [0, 1][x == i]))
                group_data_list.append(group_data[self.Factor].apply(lambda x : [[0, 1][x == 6], 1][x == 5]))
                group_data = pd.concat(group_data_list, axis=1)
                industry_data_list.append(group_data)
            industry_data = pd.concat(industry_data_list, axis=0)
            industry_data = industry_data / industry_data.sum()
            date_data_list.append(industry_data)
        date_data = pd.concat(date_data_list, axis=0)
        date_data.columns = ['group_%d' % i for i in range(1, 6)]
        self.MonotonyData = pd.concat([self.MonotonyData, date_data], axis=1).set_index('trade_date')

    def factor_test(self, factor):
        self.factor_regression(factor)
        print('Regression Finished!')
        self.monotony_group_div()
        print('Group Div Finished!')
        self.group_return_cal()
        print('Monotony Test Finished!')
        print('Result:')
        T = self.TestData['t']
        IC = self.TestData['ic']
        BETA = self.TestData['beta']
        T_ABS = self.TestData['t_abs']
        IC_ABS = self.TestData['ic_abs']

        print ("T值绝对值的均值为：" + str(T_ABS.mean()))
        print ("T值绝对值大于等于2的概率是：" + str(len([a for a in T_ABS.tolist() if a >= 2]) / len(T_ABS)))
        print ("T值大于0的概率是：" + str(len([a for a in T.tolist() if a > 0]) / len(T)))

        print ("IC值的均值为：" + str(IC.mean()))
        print ("IC值绝对值的均值为：" + str(IC_ABS.mean()))
        print ("IC值的标准差为：" + str(IC.std()))
        print ("IC值大于0的占比为：" + str(len([a for a in IC.tolist() if a > 0]) / len(IC)))
        print ("IC值绝对值大于0.02的占比为：" + str(len([a for a in IC_ABS.tolist() if a > 0.02]) / len(IC_ABS)))
        print ("IR值为：" + str(IC.mean() / IC.std()))

        plt.figure(figsize=(15, 9))
        BETA.hist()
        plt.xlabel("因子收益", fontsize=25)
        plt.ylabel("频率", fontsize=25)
        plt.title("因子收益频率分布直方图", fontsize=30)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.savefig(factor + "_因子收益频率分布直方图.png", dpi=300)
        plt.show()

        plt.figure(figsize=(15, 9))
        T_ABS.hist()
        plt.xlabel("T值绝对值", fontsize=25)
        plt.ylabel("频率", fontsize=25)
        plt.title("T值绝对值频率分布直方图", fontsize=30)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.savefig(factor + "_T值绝对值频率分布直方图.png", dpi=300)
        plt.show()

        plt.figure(figsize=(15, 9))
        plt.bar(list(range(len(BETA))), BETA, color="blue")
        plt.xlabel("时间", fontsize=25)
        plt.ylabel("因子收益", fontsize=25)
        plt.title("因子收益时间序列", fontsize=30)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.savefig(factor + "_因子收益时间序列.png", dpi=300)
        plt.show()

        plt.figure(figsize=(15, 9))
        plt.bar(list(range(len(T_ABS))), T_ABS, color="blue")
        plt.axhline(2, color="r")
        plt.xlabel("时间", fontsize=25)
        plt.ylabel("T值绝对值", fontsize=25)
        plt.title("T值绝对值时间序列", fontsize=30)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.savefig(factor + "_T值绝对值时间序列.png", dpi=300)
        plt.show()

        plt.figure(figsize=(15, 9))
        plt.bar(list(range(len(IC_ABS))), IC_ABS, color="blue")
        plt.xlabel("时间", fontsize=25)
        plt.ylabel("IC值绝对值", fontsize=25)
        plt.title("IC值绝对值时间序列", fontsize=30)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.savefig(factor + "_IC值绝对值时间序列.png", dpi=300)
        plt.show()

        plt.figure(figsize=(15, 9))
        for i in range(1, 6):
            plt.plot(self.GroupReturn["group_%d"%i], label="Group %d"%i)
        plt.xlabel("时间", fontsize=25)
        plt.ylabel("", fontsize=25)
        plt.title("分组回溯累计收益率", fontsize=30)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.savefig(factor + "_分组回溯累计收益率.png", dpi=300)
        plt.legend()
