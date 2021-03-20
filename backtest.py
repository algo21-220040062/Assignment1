data = pd.read_csv('mlp7.csv',index_col=0)

DATE = list(set(data.index.tolist()))
DATE.sort()
DATE = DATE[14:]
q_DATE = DATE[1:]
q_DATE.append('2019-04-01')
portfolio_dict_1 = {}
portfolio_dict_2 = {}
for date in DATE:
    date_data = data.loc[date].copy()
    date_data = date_data.set_index('order_book_id').sort_values('y_pred')
    portfolio_dict_1[date] = date_data[10:].head(70).index.tolist()
    portfolio_dict_2[date] = date_data.tail(80).index.tolist()

portfolio_1_return = []
portfolio_2_return = []
for i in range(13):
    date = DATE[i]
    q_date = q_DATE[i]
    price_data_1 = get_price(portfolio_dict_1[date], start_date=date, end_date=q_date,
                                  fields=['close']).iloc[:-1]
    price_data_2 = get_price(portfolio_dict_2[date], start_date=date, end_date=q_date,
                                  fields=['close']).iloc[:-1]
    weight_1 = 1 / price_data_1.iloc[0] / len(portfolio_dict_1[date])
    weight_2 = 1 / price_data_2.iloc[0] / len(portfolio_dict_2[date])
    price_data_1 = price_data_1.mul(weight_1).sum(1)
    price_data_2 = price_data_2.mul(weight_2).sum(1)
    if portfolio_1_return != []:
        price_data_1 = price_data_1 * portfolio_1_return[-1].iloc[-1]
    if portfolio_2_return != []:
        price_data_2 = price_data_2 * portfolio_2_return[-1].iloc[-1]
    portfolio_1_return.append(price_data_1)
    portfolio_2_return.append(price_data_2)
portfolio_2_1 = pd.concat(portfolio_1_return, axis=0)
portfolio_2_2 = pd.concat(portfolio_2_return, axis=0)

hs300 = get_price('000300.XSHG','2018-03-01','2019-03-29',fields=['close'])
hs300 = hs300 / hs300[0]



plt.figure(figsize=(15, 9))
plt.plot(portfolio_2_1-1, color='red', label='Portfolio 1')
plt.plot(portfolio_2_2-1, color='green', label='Portfolio 2')
plt.plot(portfolio_2_1 - portfolio_2_2, color='blue', label='Portfolio 3')
plt.plot(hs300-1, color='k', label='HS300')
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.legend()
