# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 12:21:49 2015

@author: yiyuezhuo
"""

import jieba
import jieba.analyse
import csv
import craw2
import pickle
from yiyuezhuo_tool import Downloader,Report
import math
import matplotlib.pylab as plt
import statsmodels.api as sm
import numpy as np
import os

#from functools import partial

f=open('18-5.txt','r')
s=f.read()
f.close()

ss=jieba.analyse.extract_tags(s)

def keyword(filename,withWeight=False):
    f=open(filename,'r')
    s=f.read().decode('utf-8')
    f.close()
    ss=jieba.analyse.extract_tags(s,withWeight=withWeight)
    return ss

def show(l):
    for i in l:
        print i
def list_encode(l):
    ll=[i.encode('utf8') for i in l]
    return ll

def valid():
    return [str(i)+str(j) for i in range(15,19) for j in (range(2,7) if i!=18 else range(2,6))]

def toCSV(data,name='out.csv'):
    ite=valid()
    f=open(name,'wb')
    for i in ite:
        writer=csv.writer(f)
        writer.writerow([d.encode('gbk') for d in data[i]])
    f.close()
    
def lazy_assign(dic,dom,f):
    #这个函数试图将dic可以映射所有dom里的值，如果没有的话就通过f传key制造一个更新dic
    for key in dom:
        if not(dic.has_key(key)):
            dic[key]=f(key)
    return dic
    
def scale_word(word_set,scale1,scale2,dic=None):
    dic={} if dic==None else dic
    for word in word_set:
        try:
            if not(dic.has_key(word)):
                dic[word]=craw2.match(word,scale1,scale2)
                print 'finished %.3f'%(len(dic)/float(len(word_set)))
            else:
                print 'pass'
        except KeyboardInterrupt:
            print 'interupt'
            return dic
        except:
            print 'not finished'
            return dic
    return dic
    
def scale_word_wrap(word_set,scale1,scale2,dic=None):
    '''这个方法相比起原来的方法是操作性的而不是赋值性的'''
    dic={} if dic==None else dic
    for word in word_set:
        try:
            if not(dic.has_key(word)):
                dic[word]=craw2.match(word,scale1,scale2)
                print 'finished %.3f'%(len(dic)/float(len(word_set)))
            else:
                print 'pass'
        except KeyboardInterrupt:
            print 'interupt'
            return dic
        except:
            print 'not finished'
            return dic
    return dic
    
def legal(dic,pattern):
    '''
    l1=[dic[('+','+','+')]]
    l2=[dic[('?','+','+')],dic[('+','?','+')],dic[('+','+','?')]]
    l3=[dic[('+','?','?')],dic[('?','+','?')],dic[('?','?','+')]]
    '''
    #min_block=dic[pattern] if min_block==None else min_block
    if pattern.count('+')==1:
        return True
    else:
        for i in range(3):
            if pattern[i]=='+':
                new_pattern=list(pattern)
                new_pattern[i]='?'
                if dic[new_pattern]<dic[pattern]:
                    return False
                else:
                    return legal(dic,new_pattern)
def weight_dec(dic):
    for key,value in dic.items():
        left=value[('+','+','?')]
        right=value[('+','?','+')]
        dic[key]['score']=math.log(float(left)/right)
    return dic
def score_partial(dic,p1=('+','+','?'),p2=('+','?','?')):
    for key,value in dic.items():
        left=value[p1]
        right=value[p2]
        dic[key]['score']=float(left)/right
    return dic

def rank(data,scale,mode=0,weights=None):
    '''data是各会关键字记录，scale是关键字对应权重等'''
    idl=valid()
    sl=[]
    for iid in idl:
        word_l=data[iid]
        score=0.0
        for i in range(len(word_l)):
            word=word_l[i]
            #print word
            if weights!=None:
                weight=weights[i]
            elif mode==0:
                weight=len(word_l)-i
            elif mode==1:
                weight=1
            score+=scale[word.encode('utf-8')]['score']*weight
        sl.append(score)
    return idl,sl
def rank_show(idl,sl):
    idll=[int(i) for i in idl]
    plt.plot(idll,sl,'o')
    plt.show()
    
def regress(x,y,press=False):
    x=sm.add_constant(x)
    results = sm.OLS(y, x).fit()
    if not(press):
        print results.summary()
    return results

def analyse(data,scale,mode,rank_mode=0,weights=None):
    words=scale.values()[0]['words']
    if mode==0:
        p1=('+','+','?')
        p2=('+','?','?')
        print words[1],'/','keyword'
    elif mode==1:
        p1=('+','?','+')
        p2=('+','?','?')
        print words[2],'/','keyword'
    elif mode==2:
        p1=('+','+','?')
        p2=('?','+','?')
        print words[1],'/',words[1]
    elif  mode==3:
        p1=('+','?','+')
        p2=('?','?','+')
        print words[2],'/',words[2]
    print 'Rank mode:',rank_mode,'Origin weights:',weights!=None
    scale=score_partial(scale,p1=p1,p2=p2)
    idl,sl=rank(data,scale,mode=rank_mode,weights=weights)
    r=regress(range(len(sl)),sl)
    plt.plot(sl,'o',r.predict(),'b-')
    plt.show()

def analyse_cache(data,scale,mode,rank_mode=0,weights=None,report=None):
    #这个版本返回一个可extend的序列
    words=scale.values()[0]['words']
    if mode==0:
        p1=('+','+','?')
        p2=('+','?','?')
        report.log( words[1]+'/'+'keyword')
    elif mode==1:
        p1=('+','?','+')
        p2=('+','?','?')
        report.log(words[2]+'/'+'keyword')
    elif mode==2:
        p1=('+','+','?')
        p2=('?','+','?')
        report.log(words[1]+'/'+words[1])
        #print words[1],'/',words[1]
    elif  mode==3:
        p1=('+','?','+')
        p2=('?','?','+')
        report.log(words[2]+'/'+words[2])
        #print words[2],'/',words[2]
    report.log('Rank mode:'+str(rank_mode)+'Origin weights:'+str(weights!=None))
    scale=score_partial(scale,p1=p1,p2=p2)
    idl,sl=rank(data,scale,mode=rank_mode,weights=weights)
    r=regress(range(len(sl)),sl,press=True)
    
    report.log(r.summary(),case='summary')
    '''
    plt.plot(sl,'o',r.predict(),'b-')
    plt.show()
    '''
    fig, ax = plt.subplots( nrows=1, ncols=1 )  # create figure & 1 axis
    ax.plot(sl,'o',r.predict(),'b-')
    report.log_image(fig)
    
    

def total_analyse(data,dirname='beifen'):
    pl=os.listdir(dirname)
    for p in pl:
        path=dirname+'\\'+p
        f=open(path,'rb')
        scale=pickle.load(f)
        f.close()
        for i in range(4):
            print '* * * * '*6
            analyse(data,scale,i)
            print '* * * * '*6
            
def total_analyse_cache(data,dirname='beifen',report=None):
    report=report if report!=None else Report()
    pl=os.listdir(dirname)
    for p in pl:
        path=dirname+'\\'+p
        f=open(path,'rb')
        scale=pickle.load(f)
        f.close()
        for i in range(4):
            report.log( '* * * * '*6)
            analyse_cache(data,scale,i,report=report)#修改了report状态
            report.log( '* * * * '*6)
    return report

def total_report(data,dirname='beifen'):
    report=Report()
    total_analyse_cache(data,dirname,report)
    return report
    
    
    

    
s18_4=keyword('18-4.txt')
s18_5=keyword('18-5.txt')
data={}

for i in range(15,19):
    for j in (range(2,7) if i!=18 else range(2,6)) :
        name='data\\'+str(i)+'-'+str(j)+'.txt'
        #value=keyword(name)
        value,weights=zip(*keyword(name,True))
        data[str(i)+str(j)]=value
        data[int(str(i)+str(j))]=value
word_set=list(set(reduce(lambda x,y:x+y,data.values())))

command='test'

if command=='reset':
    scale=scale_word(list_encode(word_set),'资本主义','社会主义')
elif command=='download':
    f=open('scale','rb')
    scale=pickle.load(f)
    f.close()
    scale=scale_word(list_encode(word_set),'资本主义','社会主义')
elif command=='ready':
    f=open('scale','rb')
    scale=pickle.load(f)
    f.close()

#downloader=Downloader('minshengkongbuzhuyi',dom=list_encode(word_set),static_arg=['民生','恐怖主义'])
downloader=Downloader('renquanwuran',dom=list_encode(word_set),static_arg=['民生','恐怖主义'])

downloader.call=craw2.match
#downloader.create()
#downloader.load()
#downloader.download()
#downloader.do()

scale=downloader.data
dom=downloader.dom
#weight_dec(scale)
#idl,sl=rank(data,scale)
#regress(range(len(sl)),sl)
report=total_report(data)