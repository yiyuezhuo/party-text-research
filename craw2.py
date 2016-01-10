# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 19:16:14 2015

@author: yiyuezhuo
"""
data_case='''q: 资本主义 社会主义 发展
query:"资本主义" "社会主义" "发展" 
fieldtitle:
fieldcontent:
fieldstripurl:
bstype:
ie:utf8
include:checkbox
sitequery:
located:0
tro:off
filetype:
num:10'''
#baidu_ip='119.75.218.70:80'
baidu_ip='http://www.sogou.com/web'
def dict_format(s):
    sl=[ss.split(':') for ss in s.split('\n')]
    dic={sss[0]:sss[1] for sss in sl}
    return dic
def fff(s):
    f=open('fff.html','w')
    f.write(s)
    f.close()
    webbrowser.open('fff.html')


from itertools import product
import requests
from bs4 import BeautifulSoup
import webbrowser
import urllib


def join(s1,s2,edge=''):
    if s1=='':
        return edge+s2+edge
    else:
        return s1+' '+edge+s2+edge
def seq(n):
    chars=['+','?']
    return [i for i in product(*([chars]*n)) if '+' in i]
def get(wl,pl):
    data=dict_format(data_case)
    data['q']=''
    data['query']=''
    for i in range(len(pl)):
        word=wl[i]
        p=pl[i]
        if p=='+':
            data['q']=join(data['q'],word)
            data['query']=join(data['query'],word,'"')
        elif p=='-':
            data['q']=join(data['q4'],word)
    #r=requests.get(url=baidu_ip,data=data)
    body=urllib.urlencode(data)
    ##rr=requests.get(url=baidu_ip+'?'+r.request.body)
    rr=urllib.urlopen(baidu_ip+'?'+body)
    rr.content=rr.read()
    return rr
def refine(html):
    soup=BeautifulSoup(html)
    node=soup.findAll(attrs={'id':"scd_num"})[0]
    nl=[i for i in node.text if i in '0123456789']
    return int(''.join(nl))
    
        
def match(w1,w2,w3):
    rd={'words':(w1,w2,w3)}
    pattern=seq(3)
    for p in pattern:
        #print p
        r=get((w1,w2,w3),p)
        n=refine(r.content)
        rd[p]=n
    return rd
    
