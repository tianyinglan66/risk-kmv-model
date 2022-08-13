import numpy as np
from pandas.tseries.offsets import MonthEnd
from scipy import optimize
import time

import multiprocessing as mp
import pandas as pd
import os
import math

from KMVmodel import *

InputFolder = 'Input'
OutputFolder = 'Output'
TEND = 1

FIN_columns = {'统一编号':'TAXNUM',
               '简称'：'CNAME'，
               'TSE产业别'：'BTYPE'，
               '上市别'：'PUB'，
               '年/月'：'FIN_DATE'，
               '流动负债'：'CULI'，
               '非流动负债'：'NCLI'，
               '应付公司债－非流动'：'LTDB'，
               '负债总额'：'TOLI'，
               '资产总额'：'TOAS'，
               '合并总损益'：'NI'，
               '股东权益总额'：'BE'，
               '营业收入净額'：'Sales'，
               '利息支出率'：'ID_OI'}



STK_columns = {'证券代码'：'STKNO'，
'简称'：'CNAME'，
'统一编号'：'TAXNUM'，
'年月日'：'STK_DATE'，
'收盘价（元）'：'P'，
'流通在外股数（千股）'：'Share'，
'市值（百万元）'：'E'，
'收盘价（元）_adj'：'P_adj'}
def Data(): 
    myData = pd.HDFStore(os.path.join(InputFolder,'myData.h5'),'a')
    df_FIN = myData.get('FIN')
    df_STK = myData.get('STK')
    df_FIN_groupby = myData.get('FIN_groupby')
    df_STK_groupby = myData.get('STK_groupby')



    df_FIN = df_FIN[FIN_columns].rename(columns = FIN_columns)

    df_FIN['NI_TA'] = df_FIN['NI'] / df_FIN['TOAS']
    df_FIN['E_TL'] = df_FIN['BE'] / df_FIN['TOLI']
    df_FIN['TL_TA'] = df_FIN['TOLI'] / df_FIN['TOAS']
    df_FIN['S_TA'] = df_FIN['Sales'] / df_FIN['TOAS']
    df_FIN['IE_OI'] = df_FIN['ID_OI'] / 100


    df_STK = df_STK[STK_columns].rename(columns = STK_columns)
    df_STK_groupby = df_STK_groupby.reset_index()


    ID_F = list(df_FIN_groupby['統一編號'].unique())
    ID_S = list(df_STK_groupby['統一編號'].unique())
    ID = list(set(ID_F) & set(ID_S)- {'',np.nan}) 

    df = df_FIN_groupby.query('統一編號 in {}'.format(ID))
    df = df.join(df_STK_groupby.set_index('統一編號')[['證券代碼','年月日_min', '年月日_max']], lsuffix = '_FIN', rsuffix = '_STK',on = '統一編號')
        

    df = df[['簡稱','上市別','TSE 產業別','會計月份','統一編號','年/月_min','年/月_max','證券代碼','年月日_min','年月日_max']]
    df = df.reset_index().drop(columns='index').sort_values('證券代碼')
    df['KMV_start'] = df[['年/月_min','年月日_min']].apply(pd.to_datetime).apply({'年/月_min':lambda x:x+pd.DateOffset(months=3),'年月日_min':lambda x :x}).max(axis=1)

    df['KMV_end'] = df[['年/月_max','年月日_max']].apply(pd.to_datetime).apply({'年/月_max':lambda x:x+pd.DateOffset(months=3),'年月日_max':lambda x :x}).min(axis=1)

    df = df.set_index('統一編號')


    df_FIN.loc[:,'FIN_DATE'] = pd.to_datetime(df_FIN['FIN_DATE']) + pd.DateOffset(months = 3)
    df_STK.loc[:,'STK_DATE'] = pd.to_datetime(df_STK['STK_DATE'])
    df_FIN = df_FIN.set_index(['TAXNUM','FIN_DATE'])
    df_STK = df_STK.set_index(['TAXNUM','STK_DATE'])


    ID_KMV = df.query('上市別 == "TSE"')

    myData.close()
    with pd.HDFStore(os.path.join(OutputFolder,'KMV_Data.h5')) as myData:
        myData.put('df_FIN',df_FIN,format='t')
        myData.put('df_STK',df_STK,format='t')
        myData.put('ID_KMV',ID_KMV,format='t')



Data()