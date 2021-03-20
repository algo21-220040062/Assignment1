# -*- coding: utf-8 -*-
"""
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#1.取数
path = "./"
data = pd.read_excel(path+'data.xlsx')

vin = data.iloc[:,1]#指数净值
vst = data.iloc[:,2]#股票净值

#模拟生成数，先生成正态分布的收益率，再反推导出值
import numpy.random as npr

rin=npr.normal(0,0.015,999)#指数收益率
rst=npr.normal(0,0.02,999)#股票收益率
#股票和指数的初始值
data=pd.DataFrame(index=range(1000),columns=["指数","股票A"])
data.iloc[0,0]=1000
data.iloc[0,1]=5
for i in range(999):
    data.iloc[i+1,0] = data.iloc[i,0]*(1+rin[i])
    data.iloc[i+1,1] = data.iloc[i,1]*(1+rst[i])

#这里生成了随机的data，重新开始操作
vin = data.iloc[:,0].tolist()#指数净值
vst = data.iloc[:,1].tolist()#股票净值
#这里用对数收益率
data=data/data.shift(1)

rin=np.log(data.iloc[1:,0].tolist())
rst=np.log(data.iloc[1:,1].tolist())

#2.最大回撤

def maxhuiche(vst):
    minv=1
    for i in range(len(vst)):
        mid=min(0,vst[i]-max(vst[:i+1]))/max(vst[:i+1])
        if mid < minv:
            minv=mid
    return -minv

print("股票A的最大回撤为: -%.2f%%"%(maxhuiche(vst)*100))

#3.beta
beta=(np.cov(list(rst-rin),rin)/np.std(rin))[0][1]

#*****************************************************
#以下是组合收益测算的部分

tstr='201101'  
stock='000912'

#生成一个字典来储存收益率数据，从而加快寻找速度
ret_data={}
for i in range(2010,2016):
    for j in ['01','02','03','04','05','06','07','08','09','10','11','12']:
        try:
           ret_data[str(i)+j] = pd.read_excel(path+'A股除ST月收益率/'+str(i)+j+'.xlsx')
        except:
            pass


def read_ret(tstr,stock):#返回收益率
    middata = ret_data[tstr]
    try:
        return middata[middata['Stkcd']==int(stock)].iloc[0,1]#返回对应收益率的值
    except:
        return 0

call_his_data=pd.read_excel(path+'组合收益测算'+".xlsx",sheet_name="历史多头组合")
put_his_data=pd.read_excel(path+'组合收益测算'+".xlsx",sheet_name="历史空头组合")
weight_data=pd.read_excel(path+'组合收益测算'+".xlsx",sheet_name="多空组合权重").iloc[:-1,:]
zz800=pd.read_excel(path+'组合收益测算'+".xlsx",sheet_name="中证800指数收盘价")

#填充收益率数据
call_ret=pd.DataFrame(index=call_his_data.index,columns=call_his_data.columns)
for i in call_his_data.columns:
    for j in call_his_data.index:
        call_ret.loc[j,i] = read_ret(str(i)[:6],call_his_data.loc[j,i])
        
put_ret=pd.DataFrame(index=put_his_data.index,columns=put_his_data.columns)
for i in put_his_data.columns:
    for j in put_his_data.index:
        put_ret.loc[j,i] = -1*read_ret(str(i)[:6],put_his_data.loc[j,i])

call_put_ret=call_ret+put_ret#多空组合收益


#生成中证800的月收益率序列
mon_start_i=0
mon_end_i=0
zz800_rl=[]
for i in range(1,len(zz800)): 
    if str(zz800.iloc[i,0])[5:7] != str(zz800.iloc[i-1,0])[5:7]:
       mon_end_i = i-1
       zz800_rl.append(np.log(zz800.iloc[mon_end_i,1]/zz800.iloc[mon_start_i,1]))
       mon_start_i = i
zz800_rl.append(np.log(zz800.iloc[-1,1]/zz800.iloc[mon_start_i,1]))
 
we_call_rl = call_ret.mul(weight_data).sum()
we_put_rl = put_ret.mul(weight_data).sum()
we_callput_rl = call_put_ret.mul(weight_data).sum()
call_zz800_rl = we_call_rl-zz800_rl


nv_call = (we_call_rl+1).cumprod()
nv_put = (we_put_rl+1).cumprod()
nv_callput = (we_callput_rl+1).cumprod()
nv_callzz800 = (call_zz800_rl+1).cumprod()


ndata=pd.concat([nv_call,nv_put,nv_callput,nv_callzz800],axis=1)
ndata.columns=['call','put','call-put','call-zz800']
ndata.index=range(len(ndata))
plt.plot(ndata)
plt.legend(ndata.columns)
plt.show()

def calin(ret,base_rl):#输入收益率序列，输出对应的各类指标
    #指标包括：最大回撤、月度胜率、信息比、年化收益率、年化波动、换手率
    #最大回撤
    nv = (ret+1).cumprod().tolist()
    minv=1
    for i in range(len(nv)):
        mid=min(0,nv[i]-max(nv[:i+1]))/max(nv[:i+1])
        if mid < minv:
            minv=mid
    maxhuiche = -minv
    #月度胜率
    winrate = len(ret[ret>0])/len(ret)
    excess_ret=np.array(ret) - np.array(base_rl)
    ir = np.mean(excess_ret)/np.std(excess_ret)
    annual_yield = np.power(nv[-1],4/len(nv))-1
    annual_vol = np.std(ret)*np.sqrt(12)
    return (maxhuiche,winrate,ir,annual_yield,annual_vol)

result_call=pd.DataFrame(index=['整体','2010','2011','2012','2013','2014','2015'],columns=['最大回撤','月度胜率','信息比','年化收益率','年化波动率'])
result_put=pd.DataFrame(index=['整体','2010','2011','2012','2013','2014','2015'],columns=['最大回撤','月度胜率','信息比','年化收益率','年化波动率'])
result_callput=pd.DataFrame(index=['整体','2010','2011','2012','2013','2014','2015'],columns=['最大回撤','月度胜率','信息比','年化收益率','年化波动率'])
result_callzz800=pd.DataFrame(index=['整体','2010','2011','2012','2013','2014','2015'],columns=['最大回撤','月度胜率','信息比','年化收益率','年化波动率'])

def input_res(res,ret):#填充指标
    res.iloc[0,:]=calin(ret,zz800_rl)
    res.iloc[1,:]=calin(ret[:12],zz800_rl[:12])
    res.iloc[2,:]=calin(ret[12:24],zz800_rl[12:24])
    res.iloc[3,:]=calin(ret[24:36],zz800_rl[24:36])
    res.iloc[4,:]=calin(ret[36:48],zz800_rl[36:48])
    res.iloc[5,:]=calin(ret[48:60],zz800_rl[48:60])
    res.iloc[6,:]=calin(ret[60:],zz800_rl[60:])


input_res(result_call,we_call_rl)
input_res(result_put,we_put_rl)
input_res(result_callput,we_callput_rl)
input_res(result_callzz800,call_zz800_rl)



#为了方便计算，新建两个dataframe储存weight，index为所有股票
def turnover():#输入收益率序列输出换手率    
    call_allweight=pd.DataFrame(index=ret_data[201001]['Stkcd'],columns=range(len(call_his_data)))
    put_allweight=pd.DataFrame(index=ret_data[201001]['Stkcd'],columns=range(len(call_his_data)))
    for i in range(len(call_his_data)):
        for j in range(len(call_allweight)):
            if call_allweight.index[j] in call_his_data[:,i]:
                i_st=call_his_data[call_his_data[:,i]==call_allweight.index[j]].index
                call_allweight.iloc[j,i] = weight_data.iloc[i_st,i]
            if put_allweight.index[j] in put_his_data[:,i]:
                i_st=put_his_data[put_his_data[:,i]==put_allweight.index[j]].index
                put_allweight.iloc[j,i] = weight_data.iloc[i_st,i]
    net_value_call = call_allweight*nv_call
    net_value_put = put_allweight*nv_call
    for i in range(1,len(call_his_data.columns)):
        turnover_call=abs(net_value_call[:,i]-net_value_call[:,i-1]).sum()/nv_call[i]
        turnover_put=abs(net_value_put[:,i]-net_value_put[:,i-1]).sum()/nv_put[i]
        turnover_callput=(abs(net_value_call[:,i]-net_value_call[:,i-1]).sum()+
                          abs(net_value_put[:,i]-net_value_put[:,i-1]).sum())/nv_callput[i]
    return turnover_call,turnover_put,turnover_callput
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
    