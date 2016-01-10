# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 15:50:34 2015

@author: yiyuezhuo
"""
import webbrowser
import pickle
import traceback
import random
import matplotlib.image as mpimg
import matplotlib.pylab as plt
from pyquery import PyQuery as pq
import os


def dict_format(s):
    sl=[ss.split(':') for ss in s.split('\n')]
    dic={sss[0]:sss[1] for sss in sl}
    return dic

def fff(s):
    f=open('fff.html','w')
    f.write(s)
    f.close()
    webbrowser.open('fff.html')

class Downloader(object):
    '''它基本维持一个字典，包括下载的异常管理以及类惰性求值性'''
    def __init__(self,filename,data=None,dom=None,static_arg=None,call=None,trace=1):
        self.filename=filename
        self.data={} if data==None else data
        self.dom=[] if dom==None else dom
        self.static_arg=[] if static_arg==None else static_arg
        self.call=call
        self.trace=trace#trace越高表示需要追踪的信息越多.0被定义为完全不追踪
        self.temp_save_percent=0.1
    def create(self):
        f=open(self.filename,'wb')
        f.close()
    def load(self):
        f=open(self.filename,'rb')
        self.data=pickle.load(f)
        f.close()
    def save(self):
        f=open(self.filename,'wb')
        pickle.dump(self.data,f)
        f.close()
    def percent(self,m,n,text=''):
        return '%s %f.3' %(text,float(m)/n)
    def print_trace(self,s,trace):
        if self.trace>=trace:
            print s
    def download(self):
        for var_arg in self.dom:
            try:
                if random.random()<self.temp_save_percent:
                    print 'temp saving'
                    self.save()
                if not(self.data.has_key(var_arg)):
                    #call应该被实现为赋值式的
                    self.data[var_arg]=self.call(var_arg,*self.static_arg)
                    self.print_trace(self.percent(len(self.data),len(self.dom),'fin'),1)
                else:
                    self.print_trace(self.percent(len(self.data),len(self.dom),'pass'),1)
            except KeyboardInterrupt:
                print 'Manually Exit'
                print 'dealing'+str(var_arg)
                break
            except Exception:
                traceback.print_exc()  
                #print msg
                print 'Unknow BUG'
                print 'dealing'+str(var_arg)
                break
        print 'saving'
        self.save()
        print self.percent(len(self.data),len(self.dom),'fin')
        return self.data
    def do(self):
        try:
            self.load()
        except:
            self.data={}
        self.download()
        
                    
class Report(object):
    def __init__(self,temp_file_name='Report_temp.html',temp_dir_name='report_dir'):
        self.table=[]
        self.temp_file_name=temp_file_name
        self.temp_dir_name=temp_dir_name
        self.index=0
        try:
            os.listdir(temp_dir_name)
        except:
            os.mkdir(temp_dir_name)
    def log(self,data,case='text'):
        #这里暂时图片保存不是这里处理，不然耦合太强。记录图片时就是传地址
        self.table.append({'type':case,'data':data})        
    def out_print(self):
        for record in self.table:
            if record['type']=='text' or record['type']=='summary':
                print record['data']
            elif record['type']=='image':
                img = mpimg.imread(record['data'])
                plt.imshow(img)
                plt.show()
    def as_html(self,css=True):
        d = pq("<html></html>")
        d.append('<head></head>')
        d.append('<body></body>')
        
        head=d('head')
        body=d('body')

        head.append('<meta charset="UTF-8">')
        if css:
            link='<link type="text/css" rel="stylesheet" href="test.css">'
            head.append(link)
        #head=pq('<head></head>')
        #meta=pq('<meta charset="UTF-8">')
        #body=pq('<body></body>')
        #d.append('<body></body>')
        #meta=pq('<meta charset="UTF-8">')
        #head.append(meta)
        #d.append(head)
        #d.append(body)
        for record in self.table:
            if record['type']=='text':
                body.append('<p>'+record['data'].decode('utf8')+'</p>')
            elif record['type']=='image':
                body.append('<img src='+record['data']+'>')
            elif record['type']=='summary':
                body.append(record['data'].as_html())
        return d.outer_html()
        '''
        f=open(self.temp_file_name,'w')
        f.write(d.outer_html())
        f.close()
        if not(press):
            webbrowser.open(self.temp_file_name)
        '''
    def out_html(self,press=False):
        html=self.as_html()
        f=open(self.temp_file_name,'w')
        f.write(html.encode('utf8'))
        f.close()
        if not(press):
            webbrowser.open(self.temp_file_name)
    def get_index(self):
        self.index+=1
        return self.index
    def get_path(self,postfix='.png'):
        index=self.get_index()
        path=self.temp_dir_name+'\\'+str(index)+postfix
        return path
    def log_image(self,fig):
        path=self.get_path()
        fig.savefig(path)
        plt.close()
        self.log(path,case='image')

                
        
                
                
            
