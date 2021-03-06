import pandas as pd
import ctypes#弹窗提醒
import tushare as ts
import tushare.stock.indictor as idx
#下面用于判断筛选出来的个股是否正处于调查中
codes_bdc=pd.read_excel('调查中企业.xlsx').code.tolist() #读取被调查股票代码表
codes_bdc=[str(x) for x in codes_bdc]#把数值转字符串code
codes_dbl=[] #底背离股票列表
#codes=ts.get_gem_classified().code.tolist()#取得创业板列表
codes=ts.get_sme_classified().code.tolist()#取得中小板代码列表
#codes=codes_bdc
#codes_dbl=[]
for code in codes:
    #print(code)
    #print('-------')
    data = ts.get_k_data(code, start="2018-01-01", end="2018-07-25",ktype='30')#取得日线数据
    if (len(data)!=0):
        macd,diff,dea=idx.macd(data,12,26,9,'close')#取得该区段内的MACD各值
        macd = macd * 2 #行情软件显示的MACD是计算出的2倍
        data['diff2']=diff #给data增加diff列，因diff为保留关键字，所以列名用diff2代替
        data['dea'] = dea  # 给data增加dea列
        df_diff_dea=pd.DataFrame(diff-dea,index=data.index,columns=['diff_dea']) #计算diff-dea差值的DataFrame，用以判断波形是顶背离还是底背离，index同data
        df_diff_dea['date'] = data.date #增加date时间列
        dftemp=df_diff_dea[df_diff_dea.diff_dea>0] #diff-dea>0 则diff在dea上，用于判断顶背离
        dftemp2=df_diff_dea[df_diff_dea.diff_dea<0]#diff-dea<0 则diff在dea下，用于判断底背离
        dftemp2_down=dftemp2.sort_index(ascending=False) #倒序，从后往前
        ls=dftemp2_down.index.tolist() #转成列表，比较不连续段，不连续段用于分割2个不同的底背离
        ls_dbl=[] #用于保存底背离区段的index
        down_id_end=0 #diff在dea之下的起始位置
        for i in range(len(ls)-1):#找出不连续Diff在DEA下面的开始位置
            if ((ls[i]-ls[i+1])>1): #比较相邻的2个index是否连续，不连续则是分隔点
                #print('------------------')
                #print(dftemp2_down.iloc[i].date)
                #print(ls[i])  #分割点起始位置
                #print(dftemp2_down.iloc[down_id_end].date)
                #print(ls[down_id_end]) #分隔结束位置
                #print('------------------')
                ls_dbl.append([ls[i], ls[down_id_end]])
                down_id_end=i+1 #上一个波段结束位置为上面循环i-1


    #判断相邻2个波谷的Diff、low的值是否形成背离
        if(len(ls_dbl)>=2):
            dbl1_diff_min=data[ls_dbl[0][0]:ls_dbl[0][1]+1].diff2.min()
            dbl1_low_min=data[ls_dbl[0][0]:ls_dbl[0][1]+1].low.min()

            dbl2_diff_min=data[ls_dbl[1][0]:ls_dbl[1][1]+1].diff2.min()
            dbl2_low_min=data[ls_dbl[1][0]:ls_dbl[1][1]+1].low.min()

            if(dbl2_low_min>dbl1_low_min)&(dbl2_diff_min<dbl1_diff_min)&(data.iloc[-1].diff2>dbl1_diff_min)&(abs(data.iloc[-1].dea-data.iloc[-1].diff2)<0.1): #背离且最新diff高于低点diff，即有反身向上趋势
                codes_dbl.append(code)
    #else:
        #print(code+'is new stock')
for code in codes_dbl:
    if code in codes_bdc:
        print(code+'该股票处于被调查状态')
    else:
        print(code)

'''
得到创业板各股周涨幅情况表
for code in codes: #codes 可通过tushare获得
    #print(code)
    #print('-------')
    datanew=ts.get_hist_data(code, start="2018-07-16", end="2018-07-20",ktype='W')
    datanew['code']=code
    data = data.append(datanew)  
'''

