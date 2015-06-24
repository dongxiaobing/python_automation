#!/bin/python
#coding=utf-8
"""
修改prodviewdb.products_core_search表中指定producu_id的publish_date为1920-01-01 00:00:00
修改单品库ProductDB.Products_Core表中指定的product_id的publish_date为0001-01-01 00:00:00
修改单品库中的ProductDB.Products_Core中的last_changed_date为2015-05-08 09:00:00
修改搜索数据库prodviewdb.process_status中process_name为'Dang.SearchDataArch.Service.ProductCoreSync'的process_last_date为2015-05-08 08:50:00
等待单品数据同步
查询prodviewdb.products_core_search表中指定producu_id的publish_date是否修改为1970-01-01 00:00:00
"""

import sys   
import urllib2
import re
reload(sys)  
sys.setdefaultencoding('utf8')  
import MySQLdb
import json
import unittest
from time import sleep
import datetime
import time
from xml.etree import ElementTree
from lxml import etree as ET
from io import BytesIO
import urllib

class TestProject3980PublishDate(unittest.TestCase):
    def setUp(self):
        self.sql_limit_num=10
        self.host_search="10.255.254.22"
        self.host_product="10.255.255.22"
        self.db_search="prodviewdb"
        self.db_product="ProductDB"
        self.user="writeuser"
        self.passwd="ddbackend"
        self.publish_date_NULL="NULL"
        self.publish_date_finally="1970-01-01 00:00:00"
        self.publish_date_0001="0001-01-01 00:00:000"
        self.publish_date_0000="0000-00-00 00:00:000"
        self.publish_date_small="1909-12-31 23:59:59"
        self.publish_date_equal="1910-01-01 00:00:00"
        self.publish_date_big="1910-01-01 00:00:01"
        self.last_changed_date='2015-05-07 00:01:00'
        self.process_last_date='2015-05-07 00:00:00'
    def tearDown(self):
        pass
    def updateinfo_to_mysql(self,sql_cmd,host,user,passwd,db):
        #print sql_cmd
        conn=MySQLdb.connect(host=host,user=user,passwd=passwd,db=db,charset="utf8")
        cursor = conn.cursor()
        n = cursor.execute(sql_cmd)
        conn.commit()
        cursor.close()
        conn.close()
    
    def getinfo_from_mysql(self,sql_cmd,host,user,passwd,db):
        #print sql_cmd
        product_info=[]
        conn=MySQLdb.connect(host=host,user=user,passwd=passwd,db=db,charset="utf8")
        cursor = conn.cursor()
        n = cursor.execute(sql_cmd)
        for row in cursor.fetchall():
            for i in row:    
                product_info.append(i)
                #print "!",i
        cursor.close()
        #cursor.commit()
        conn.close()
        return product_info
    def get_product_id_list(self,db,table,host,user,passwd,flag="nonull"):
        """获取产品id"""
        if flag=="NULL":
            sql_get_product_id="select product_id from %s  where publish_date is null order by product_id desc limit 50;" % table
            product_id_list=self.getinfo_from_mysql(sql_get_product_id,host,user,passwd,db)
            return product_id_list
        else:
            sql_get_product_id="select product_id from %s order by product_id desc limit 50;" % table
            product_id_list=self.getinfo_from_mysql(sql_get_product_id,host,user,passwd,db)
            return product_id_list
    def get_publish_date(self,product_id_list,db,table,host,user,passwd):
        """获取产品publish_date"""
        sql_get_product_id="select publish_date from %s where product_id=%s;" % (table,product_id_list[0])
        publish_date=self.getinfo_from_mysql(sql_get_product_id,host,user,passwd,db)
        return publish_date
    def get_publish_date_all(self,product_id_list,db,table,host,user,passwd):
        """获取产品publish_date"""
        publist_date_list=[]
        for i in product_id_list:
            sql_get_product_id="select publish_date from %s where product_id=%s;" % (table,i)
            publish_date=self.getinfo_from_mysql(sql_get_product_id,host,user,passwd,db)
            #print "$$$$$$"
            #print publish_date
            if publish_date == [None]:
                return ["NULL"]
            elif publish_date==[datetime.datetime(1, 1, 1, 0, 0)]:
                return "0001-01-01 00:00:00"
            else:
                publish_date=publish_date[0].strftime("%Y-%m-%d %H:%M:%S")
                publist_date_list.append(publish_date)
            #print publist_date_list
        publist_date_set=set(publist_date_list)
        publist_date=list(publist_date_set)
        return publist_date
    
    def delete_product_to_prodviewdb(self,product_id_list):
        delete_product_to_prodviewdb="delete from products_core_search where product_id=%s;" % product_id_list[0]
        self.updateinfo_to_mysql(delete_product_to_prodviewdb,self.host_search,self.user,self.passwd,self.db_search)
    
    def update_publish_date_to_prodviewdb(self,product_id_list,publish_date):
        #修改搜索数据库prodviewdb.products_core_search的publish_date
        #print "修改搜索数据库prodviewdb.products_core_search的publish_date"
        for i in product_id_list:
            update_publish_date_to_prodviewdb="update products_core_search set publish_date='%s' where product_id=%s;" % (publish_date,i)
            self.updateinfo_to_mysql(update_publish_date_to_prodviewdb,self.host_search,self.user,self.passwd,self.db_search)
    def update_publish_date_to_ProductDB(self,flag_null,product_id_list,publish_date):
        #修改单品库ProductDB.Products_Core的publish_date
        #对于出版时间（publish_date字段）不为NULL，且小于或等于“1910-01-01 00:00:00”，则更改此字段为“1970-01-01 00:00:00”
        #print "修改单品库ProductDB.Products_Core的publish_date"
        if flag_null=="no":
            for i in product_id_list:
                update_publish_date_ProductDB="update Products_Core set publish_date='%s' where product_id=%s;" % (publish_date,i)
                self.updateinfo_to_mysql(update_publish_date_ProductDB,self.host_product,self.user,self.passwd,self.db_product)
        elif flag_null=="yes":
            for i in product_id_list:
                update_publish_date_ProductDB="update Products_Core set publish_date is '%s' where product_id=%s;" % (publish_date,i)
                self.updateinfo_to_mysql(update_publish_date_ProductDB,self.host_product,self.user,self.passwd,self.db_product)
        elif flag_null=="all":
                update_publish_date_ProductDB_0001="update Products_Core set publish_date='%s' where product_id=%s;" % (self.publish_date_small,product_id_list[0])
                self.updateinfo_to_mysql(update_publish_date_ProductDB_0001,self.host_product,self.user,self.passwd,self.db_product)
                update_publish_date_ProductDB_NULL="update Products_Core set publish_date='%s' where product_id=%s;" % (self.publish_date_0000,product_id_list[1])
                self.updateinfo_to_mysql(update_publish_date_ProductDB_NULL,self.host_product,self.user,self.passwd,self.db_product)
                update_publish_date_ProductDB_small="update Products_Core set publish_date='%s' where product_id=%s;" % (self.publish_date_0001,product_id_list[2])
                self.updateinfo_to_mysql(update_publish_date_ProductDB_small,self.host_product,self.user,self.passwd,self.db_product)
                update_publish_date_ProductDB_equal="update Products_Core set publish_date='%s' where product_id=%s;" % (self.publish_date_equal,product_id_list[3])
                self.updateinfo_to_mysql(update_publish_date_ProductDB_equal,self.host_product,self.user,self.passwd,self.db_product)
                update_publish_date_ProductDB_big="update Products_Core set publish_date='%s' where product_id=%s;" % (self.publish_date_big,product_id_list[4])
                self.updateinfo_to_mysql(update_publish_date_ProductDB_big,self.host_product,self.user,self.passwd,self.db_product)
        else:
            pass
    def update_process_last_date_prodviewdb(self,process_last_date):
        #初始化process_last_date from 搜索数据库prodviewdb.process_status
        #print "修改搜索数据库prodviewdb.process_status的process_last_date"
        update_process_last_date_to_prodviewdb="update process_status set process_last_date='%s' where process_name = 'Dang.SearchDataArch.Service.ProductCoreSync';" % process_last_date
        self.updateinfo_to_mysql(update_process_last_date_to_prodviewdb,self.host_search,self.user,self.passwd,self.db_search)
        
    def update_last_changed_date_ProductDB(self,last_changed_date,product_id_list):
        #修改单品库中的ProductDB.Products_Core中的last_changed_date
        #print "修改单品库中的ProductDB.Products_Core中的last_changed_date"
        for i in product_id_list:    
            #print i
            update_last_changed_date_ProductDB="update Products_Core set last_changed_date='%s' where product_id=%s;" % (last_changed_date,i)
            #print update_last_changed_date_ProductDB
            self.updateinfo_to_mysql(update_last_changed_date_ProductDB,self.host_product,self.user,self.passwd,self.db_product)
            
          
    def get_modify_date(self,db,product_id_list):
        if db=="prodviewdb":
            process_last_date_cmd="select process_last_date from process_status where process_name = 'Dang.SearchDataArch.Service.ProductCoreSync' limit 1;"
            process_last_date=self.getinfo_from_mysql(process_last_date_cmd,self.host_search,self.user,self.passwd,self.db_search)
            return process_last_date
        elif db=="ProductDB":
            last_changed_date_cmd="select last_changed_date from Products_Core where product_id=%s;" % product_id_list[0]
            #print last_changed_date_cmd
            last_changed_date=self.getinfo_from_mysql(last_changed_date_cmd,self.host_product,self.user,self.passwd,self.db_product)
            
            return last_changed_date
        else:
            pass
    def get_same_product_id(self,prodview_product_id_list,product_product_id_list):
        """根据prodview库中product_id和ProductDB的交集，获取5个产品id"""
        set1=set(prodview_product_id_list)
        set2=set(product_product_id_list)
        set3=set1 & set2
        tmp=list(set3)
        product_id_list=tmp[0:5]
        return product_id_list
            
    def check_time(self,time_from_db,time_from_manual): 
        """将datetime.datetime转成str格式"""
        str_time=time_from_db[0].strftime("%Y-%m-%d %H:%M:%S")
        self.assertEqual(str_time,time_from_manual)
    
    def check_sync_work_over(self):
        sql_cmd="select process_last_date from process_status where process_name = 'Dang.SearchDataArch.Service.ProductCoreSync';"
        process_last_date=self.getinfo_from_mysql(sql_cmd,self.host_search,self.user,self.passwd,self.db_search)
        #print process_last_date
        l_tmp=[]
        for i in process_last_date:
            tmp=i.strftime("%Y-%m-%d %H:%M:%S")
            l_tmp.append(tmp)
        if  "2015-05-07 00:00:00" not in l_tmp:
            return True
       
    
    def first_setup_get_product_id_list(self,flag="nonull"):     
        prodview_product_id_list=self.get_product_id_list(self.db_search,"products_core_search",self.host_search,self.user,self.passwd,flag)
        #print "@",prodview_product_id_list        
        product_product_id_list=self.get_product_id_list(self.db_product,"Products_Core",self.host_product,self.user,self.passwd,flag)
        #print "@",product_product_id_list       
        #get 5 product_id from prodview_product_id_list and product_product_id_list
        product_id_list=self.get_same_product_id(prodview_product_id_list, product_product_id_list)
        print "第一步获取的产品id是:%s" % product_id_list
        return product_id_list
    def second_setup_update_publish_date_to_prodviewdb(self,product_id_list,publish_date_prodviewdb):
        self.update_publish_date_to_prodviewdb(product_id_list,publish_date_prodviewdb)
        get_publish_date_from_prodviewdb=self.get_publish_date(product_id_list,self.db_search,"products_core_search",self.host_search,self.user,self.passwd)
        print "第二步更新prodviewdb.products_core_search的publish_date为：%s" % get_publish_date_from_prodviewdb
        self.check_time(get_publish_date_from_prodviewdb,publish_date_prodviewdb)
    def third_setup_update_publish_date_to_ProductDB(self,product_id_list,publish_date_ProductDB,flag="no"):
        self.update_publish_date_to_ProductDB(flag,product_id_list,publish_date_ProductDB)
        get_publish_date_from_ProductDB=self.get_publish_date(product_id_list,self.db_product,"Products_Core",self.host_product,self.user,self.passwd)
        print "第三步更新ProductDB.Products_Core的publish_date为：%s" % get_publish_date_from_ProductDB
        
        #self.check_time(get_publish_date_from_ProductDB,publish_date_ProductDB)       
    def four_setup_update_last_changed_date_ProductDB(self,last_changed_date,product_id_list):
        self.update_last_changed_date_ProductDB(self.last_changed_date,product_id_list)  
        last_changed_date=self.get_modify_date(self.db_product,product_id_list)
        print "第四步更新ProductDB.Products_Core的last_changed_date为:%s" % last_changed_date
        self.check_time(last_changed_date, self.last_changed_date)
    def five_setup_update_process_last_date_prodviewdb(self,process_last_date,product_id_list):
        self.update_process_last_date_prodviewdb(self.process_last_date)
        process_last_date=self.get_modify_date(self.db_search,product_id_list)
        print "第五步更新prodviewdb.process_status的process_last_date为:%s" % process_last_date
        self.check_time(process_last_date, self.process_last_date)

    def test_001_publish_date_smaller_than_19100101000000(self):
        print "*"*50
        print "test_001_publish_date_smaller_than_19100101000000"
        
        #11111       
        product_id_list=self.first_setup_get_product_id_list()
        #设置prodviewdb.publish_date的列publish_date为某一个值，然后检验product_id_list中的第一个产品id的publish_date为这个值，以确认更新mysql成功
        #222222
        publish_date_prodviewdb='1971-01-01 00:00:00'
        self.second_setup_update_publish_date_to_prodviewdb(product_id_list,publish_date_prodviewdb)          
        #设置ProductDB.Products_Core的列publish_date为NULL，然后检验product_id_list中的第一个产品id的publish_date为NULL，以确认更新mysql成功
        #333333
        publish_date_ProductDB=self.publish_date_small
        self.third_setup_update_publish_date_to_ProductDB(product_id_list, publish_date_ProductDB)     
        #更新ProductDB.Products_Core的last_changed_date，并且校验该值跟输入的一致性
        #4444444
        self.four_setup_update_last_changed_date_ProductDB(self.last_changed_date,product_id_list)       
        #更新prodviewdb.process_status的process_last_date，并且校验该值跟输入的一致性
        #5555555
        self.five_setup_update_process_last_date_prodviewdb(self.process_last_date,product_id_list)   
        #wait for ProductCoreSync
        while True:
            if self.check_sync_work_over():
                break
            else:
                sleep(10)
                continue 
        #publish_date of prodviewdb.products_core_search should not be changed
        publish_date=self.get_publish_date_all(product_id_list,self.db_search,"products_core_search",self.host_search,self.user,self.passwd)
        #print publish_date
        for i in publish_date:
            print "第六步校验prodviewdb.products_core_search的publish_date为:%s" % self.publish_date_finally
            self.assertEqual(i,self.publish_date_finally)
    def test_002_publish_date_equal_19100101000000(self):
        print "*"*50
        print "test_002_publish_date_equal_19100101000000"
        #11111       
        product_id_list=self.first_setup_get_product_id_list()
        #设置prodviewdb.publish_date的列publish_date为某一个值，然后检验product_id_list中的第一个产品id的publish_date为这个值，以确认更新mysql成功
        #222222
        publish_date_prodviewdb='1971-01-01 00:00:00'
        self.second_setup_update_publish_date_to_prodviewdb(product_id_list,publish_date_prodviewdb)          
        #设置ProductDB.Products_Core的列publish_date为NULL，然后检验product_id_list中的第一个产品id的publish_date为NULL，以确认更新mysql成功
        #333333
        publish_date_ProductDB=self.publish_date_equal
        self.third_setup_update_publish_date_to_ProductDB(product_id_list, publish_date_ProductDB)     
        #更新ProductDB.Products_Core的last_changed_date，并且校验该值跟输入的一致性
        #4444444
        self.four_setup_update_last_changed_date_ProductDB(self.last_changed_date,product_id_list)       
        #更新prodviewdb.process_status的process_last_date，并且校验该值跟输入的一致性
        #5555555
        self.five_setup_update_process_last_date_prodviewdb(self.process_last_date,product_id_list)   
        #wait for ProductCoreSync
        while True:
            if self.check_sync_work_over():
                break
            else:
                sleep(10)
                continue   
        #publish_date of prodviewdb.products_core_search should not be changed
        publish_date=self.get_publish_date_all(product_id_list,self.db_search,"products_core_search",self.host_search,self.user,self.passwd)
        #print publish_date
        for i in publish_date:
            print "第六步校验prodviewdb.products_core_search的publish_date为:%s" % self.publish_date_finally
            self.assertEqual(i,self.publish_date_finally) 
    def test_003_publish_date_equal_0001(self):
        print "*"*50
        print "test_003_publish_date_equal_0001"
        #11111       
        product_id_list=self.first_setup_get_product_id_list()
        #设置prodviewdb.publish_date的列publish_date为某一个值，然后检验product_id_list中的第一个产品id的publish_date为这个值，以确认更新mysql成功
        #222222
        publish_date_prodviewdb='1971-01-01 00:00:00'
        self.second_setup_update_publish_date_to_prodviewdb(product_id_list,publish_date_prodviewdb)          
        #设置ProductDB.Products_Core的列publish_date为NULL，然后检验product_id_list中的第一个产品id的publish_date为NULL，以确认更新mysql成功
        #333333
        publish_date_ProductDB=self.publish_date_0001
        self.third_setup_update_publish_date_to_ProductDB(product_id_list, publish_date_ProductDB)     
        #更新ProductDB.Products_Core的last_changed_date，并且校验该值跟输入的一致性
        #4444444
        self.four_setup_update_last_changed_date_ProductDB(self.last_changed_date,product_id_list)       
        #更新prodviewdb.process_status的process_last_date，并且校验该值跟输入的一致性
        #5555555
        self.five_setup_update_process_last_date_prodviewdb(self.process_last_date,product_id_list)   
        #wait for ProductCoreSync
        while True:
            if self.check_sync_work_over():
                break
            else:
                sleep(10)
                continue    
        #publish_date of prodviewdb.products_core_search should not be changed
        publish_date=self.get_publish_date_all(product_id_list,self.db_search,"products_core_search",self.host_search,self.user,self.passwd)
        #print publish_date
        for i in publish_date:
            print "第六步校验prodviewdb.products_core_search的publish_date为:%s" % self.publish_date_finally
            self.assertEqual(i,self.publish_date_finally) 
    def test_004_publish_date_equal_0000(self):
        print "*"*50
        print "test_004_publish_date_equal_0000"
        #11111       
        product_id_list=self.first_setup_get_product_id_list()
        #设置prodviewdb.publish_date的列publish_date为某一个值，然后检验product_id_list中的第一个产品id的publish_date为这个值，以确认更新mysql成功
        #222222
        publish_date_prodviewdb='1971-01-01 00:00:00'
        self.second_setup_update_publish_date_to_prodviewdb(product_id_list,publish_date_prodviewdb)          
        #设置ProductDB.Products_Core的列publish_date为NULL，然后检验product_id_list中的第一个产品id的publish_date为NULL，以确认更新mysql成功
        #333333
        publish_date_ProductDB=self.publish_date_0000
        self.third_setup_update_publish_date_to_ProductDB(product_id_list, publish_date_ProductDB)     
        #更新ProductDB.Products_Core的last_changed_date，并且校验该值跟输入的一致性
        #4444444
        self.four_setup_update_last_changed_date_ProductDB(self.last_changed_date,product_id_list)       
        #更新prodviewdb.process_status的process_last_date，并且校验该值跟输入的一致性
        #5555555
        self.five_setup_update_process_last_date_prodviewdb(self.process_last_date,product_id_list)   
        #wait for ProductCoreSync
        while True:
            if self.check_sync_work_over():
                break
            else:
                sleep(10)
                continue    
        #publish_date of prodviewdb.products_core_search should not be changed
        publish_date=self.get_publish_date_all(product_id_list,self.db_search,"products_core_search",self.host_search,self.user,self.passwd)
        #print publish_date
        for i in publish_date:
            print "第六步校验prodviewdb.products_core_search的publish_date为:%s" % self.publish_date_finally
            self.assertEqual(i,self.publish_date_NULL) 
    
    
    
    def test_005_publish_date_bigger_then_19100101000000(self):
        print "*"*50
        print "test_005_publish_date_bigger_then_19100101000000"
        #11111       
        product_id_list=self.first_setup_get_product_id_list()
        #设置prodviewdb.publish_date的列publish_date为某一个值，然后检验product_id_list中的第一个产品id的publish_date为这个值，以确认更新mysql成功
        #222222
        publish_date_prodviewdb='1971-01-01 00:00:00'
        self.second_setup_update_publish_date_to_prodviewdb(product_id_list,publish_date_prodviewdb)          
        #设置ProductDB.Products_Core的列publish_date为NULL，然后检验product_id_list中的第一个产品id的publish_date为NULL，以确认更新mysql成功
        #333333
        publish_date_ProductDB=self.publish_date_big
        self.third_setup_update_publish_date_to_ProductDB(product_id_list, publish_date_ProductDB)     
        #更新ProductDB.Products_Core的last_changed_date，并且校验该值跟输入的一致性
        #4444444
        self.four_setup_update_last_changed_date_ProductDB(self.last_changed_date,product_id_list)       
        #更新prodviewdb.process_status的process_last_date，并且校验该值跟输入的一致性
        #5555555
        self.five_setup_update_process_last_date_prodviewdb(self.process_last_date,product_id_list)   
        #wait for ProductCoreSync
        while True:
            if self.check_sync_work_over():
                break
            else:
                sleep(10)
                continue    
        #publish_date of prodviewdb.products_core_search should not be changed
        publish_date=self.get_publish_date_all(product_id_list,self.db_search,"products_core_search",self.host_search,self.user,self.passwd)
        #print publish_date
        for i in publish_date:
            print "第六步校验prodviewdb.products_core_search的publish_date为:%s" % self.publish_date_finally
            self.assertEqual(i,publish_date_ProductDB) 
        
    def test_006_publish_date_NULL(self):
        print "*"*50
        print "test_006_publish_date_NULL" 
        #11111
        #find the publish_date is null from ProductDB
        product_id_list=self.first_setup_get_product_id_list(flag="NULL")
        #设置prodviewdb.publish_date的列publish_date为某一个值，然后检验product_id_list中的第一个产品id的publish_date为这个值，以确认更新mysql成功
        #222222
        publish_date_prodviewdb='1971-01-01 00:00:00'
        self.second_setup_update_publish_date_to_prodviewdb(product_id_list,publish_date_prodviewdb)   
        #ProductDB.Products_Core的列publish_datey已经是为NULL，跳过第三步       
        #设置ProductDB.Products_Core的列publish_date为NULL，然后检验product_id_list中的第一个产品id的publish_date为NULL，以确认更新mysql成功
        #333333
        #ProductDB.Products_Core的列publish_datey已经是为NULL
        #publish_date_ProductDB=self.publish_date_big
        #self.third_setup_update_publish_date_to_ProductDB(product_id_list, publish_date_ProductDB)     
        #更新ProductDB.Products_Core的last_changed_date，并且校验该值跟输入的一致性
        #4444444
        self.four_setup_update_last_changed_date_ProductDB(self.last_changed_date,product_id_list)       
        #更新prodviewdb.process_status的process_last_date，并且校验该值跟输入的一致性
        #5555555
        self.five_setup_update_process_last_date_prodviewdb(self.process_last_date,product_id_list)   
        #wait for ProductCoreSync
        while True:
            if self.check_sync_work_over():
                break
            else:
                sleep(10)
                continue  
        #publish_date of prodviewdb.products_core_search should not be changed
        publish_date=self.get_publish_date_all(product_id_list,self.db_search,"products_core_search",self.host_search,self.user,self.passwd)
        #print publish_date
        for i in publish_date:
            print "第六步校验prodviewdb.products_core_search的publish_date为:%s" % i
            #print i
            self.assertEqual(i,"NULL")
    
    
    def test_007_publish_date_smaller_equal_bigger_0000_0001_then_19100101000000(self):
        print "*"*50
        print "test_007_publish_date_smaller_equal_bigger_0000_0001_then_19100101000000"    
        #11111       
        product_id_list=self.first_setup_get_product_id_list()
        #设置prodviewdb.publish_date的列publish_date为某一个值，然后检验product_id_list中的第一个产品id的publish_date为这个值，以确认更新mysql成功
        #222222
        publish_date_prodviewdb='1971-01-01 00:00:00'
        self.second_setup_update_publish_date_to_prodviewdb(product_id_list,publish_date_prodviewdb)          
        #设置ProductDB.Products_Core的列publish_date为NULL，然后检验product_id_list中的第一个产品id的publish_date为NULL，以确认更新mysql成功
        #333333
        publish_date_ProductDB=self.publish_date_big
        self.third_setup_update_publish_date_to_ProductDB(product_id_list, publish_date_ProductDB,flag="all")     
        #更新ProductDB.Products_Core的last_changed_date，并且校验该值跟输入的一致性
        #4444444
        self.four_setup_update_last_changed_date_ProductDB(self.last_changed_date,product_id_list)       
        #更新prodviewdb.process_status的process_last_date，并且校验该值跟输入的一致性
        #5555555
        self.five_setup_update_process_last_date_prodviewdb(self.process_last_date,product_id_list)   
        #wait for ProductCoreSync
        while True:
            if self.check_sync_work_over():
                break
            else:
                sleep(10)
                continue    
        #publish_date of prodviewdb.products_core_search should not be changed

        #publish_date of prodviewdb.products_core_search should not be changed
        print self.publish_date_small,self.publish_date_0000,self.publish_date_0001,self.publish_date_equal,self.publish_date_big
        for i in product_id_list:
            sql_get_product_id="select publish_date from %s where product_id=%s;" % ("products_core_search",i)
            publish_date=self.getinfo_from_mysql(sql_get_product_id,self.host_search,self.user,self.passwd,self.db_search)
            print publish_date,
        print "\n"
    def test_008_publish_date_smaller_than_19100101000000_product_not_exist_in_prodviewdb(self):
        print "*"*50
        print "test_008_publish_date_smaller_than_19100101000000_product_not_exist_in_prodviewdb"
        #11111       
        product_id_list=self.first_setup_get_product_id_list()
        #设置prodviewdb.publish_date的列publish_date为某一个值，然后检验product_id_list中的第一个产品id的publish_date为这个值，以确认更新mysql成功
        #222222
        self.delete_product_to_prodviewdb(product_id_list)
        
        """
        
        publish_date_prodviewdb='1971-01-01 00:00:00'
        self.second_setup_update_publish_date_to_prodviewdb(product_id_list,publish_date_prodviewdb)
        """          
        #设置ProductDB.Products_Core的列publish_date为NULL，然后检验product_id_list中的第一个产品id的publish_date为NULL，以确认更新mysql成功
        #333333
        publish_date_ProductDB=self.publish_date_small
        self.third_setup_update_publish_date_to_ProductDB(product_id_list, publish_date_ProductDB)     
        #更新ProductDB.Products_Core的last_changed_date，并且校验该值跟输入的一致性
        #4444444
        self.four_setup_update_last_changed_date_ProductDB(self.last_changed_date,product_id_list)       
        #更新prodviewdb.process_status的process_last_date，并且校验该值跟输入的一致性
        #5555555
        self.five_setup_update_process_last_date_prodviewdb(self.process_last_date,product_id_list)   
        #wait for ProductCoreSync
        while True:
            if self.check_sync_work_over():
                break
            else:
                sleep(10)
                continue    
        #publish_date of prodviewdb.products_core_search should not be changed
        publish_date=self.get_publish_date_all(product_id_list,self.db_search,"products_core_search",self.host_search,self.user,self.passwd)
        #print publish_date
        for i in publish_date:
            print "第六步校验prodviewdb.products_core_search的publish_date为:%s" % self.publish_date_finally
            self.assertEqual(i,self.publish_date_finally)
            
    def test_009_publish_date_equal_19100101000000_product_not_exist_in_prodviewdb(self):
        print "*"*50
        print "test_009_publish_date_equal_19100101000000_product_not_exist_in_prodviewdb"
        #11111       
        product_id_list=self.first_setup_get_product_id_list()
        #设置prodviewdb.publish_date的列publish_date为某一个值，然后检验product_id_list中的第一个产品id的publish_date为这个值，以确认更新mysql成功
        #222222
        self.delete_product_to_prodviewdb(product_id_list)
        
        """
        publish_date_prodviewdb='1971-01-01 00:00:00'
        self.second_setup_update_publish_date_to_prodviewdb(product_id_list,publish_date_prodviewdb)
        """          
        #设置ProductDB.Products_Core的列publish_date为NULL，然后检验product_id_list中的第一个产品id的publish_date为NULL，以确认更新mysql成功
        #333333
        publish_date_ProductDB=self.publish_date_equal
        self.third_setup_update_publish_date_to_ProductDB(product_id_list, publish_date_ProductDB)     
        #更新ProductDB.Products_Core的last_changed_date，并且校验该值跟输入的一致性
        #4444444
        self.four_setup_update_last_changed_date_ProductDB(self.last_changed_date,product_id_list)       
        #更新prodviewdb.process_status的process_last_date，并且校验该值跟输入的一致性
        #5555555
        self.five_setup_update_process_last_date_prodviewdb(self.process_last_date,product_id_list)   
        #wait for ProductCoreSync
        while True:
            if self.check_sync_work_over():
                break
            else:
                sleep(10)
                continue    
        #publish_date of prodviewdb.products_core_search should not be changed
        publish_date=self.get_publish_date_all(product_id_list,self.db_search,"products_core_search",self.host_search,self.user,self.passwd)
        #print publish_date
        for i in publish_date:
            print "第六步校验prodviewdb.products_core_search的publish_date为:%s" % self.publish_date_finally
            self.assertEqual(i,self.publish_date_finally)  
            
    def test_010_publish_date_biger_then_19100101000000_product_not_exist_in_prodviewdb(self):
        print "*"*50
        print "test_010_publish_date_equal_19100101000000_product_not_exist_in_prodviewdb"
        #11111       
        product_id_list=self.first_setup_get_product_id_list()
        #设置prodviewdb.publish_date的列publish_date为某一个值，然后检验product_id_list中的第一个产品id的publish_date为这个值，以确认更新mysql成功
        #222222
        self.delete_product_to_prodviewdb(product_id_list)
        
        """
        publish_date_prodviewdb='1971-01-01 00:00:00'
        self.second_setup_update_publish_date_to_prodviewdb(product_id_list,publish_date_prodviewdb)
        """          
        #设置ProductDB.Products_Core的列publish_date为NULL，然后检验product_id_list中的第一个产品id的publish_date为NULL，以确认更新mysql成功
        #333333
        publish_date_ProductDB=self.publish_date_big
        self.third_setup_update_publish_date_to_ProductDB(product_id_list, publish_date_ProductDB)     
        #更新ProductDB.Products_Core的last_changed_date，并且校验该值跟输入的一致性
        #4444444
        self.four_setup_update_last_changed_date_ProductDB(self.last_changed_date,product_id_list)       
        #更新prodviewdb.process_status的process_last_date，并且校验该值跟输入的一致性
        #5555555
        self.five_setup_update_process_last_date_prodviewdb(self.process_last_date,product_id_list)   
        #wait for ProductCoreSync
        while True:
            if self.check_sync_work_over():
                break
            else:
                sleep(10)
                continue    
        #publish_date of prodviewdb.products_core_search should not be changed
        publish_date=self.get_publish_date_all(product_id_list,self.db_search,"products_core_search",self.host_search,self.user,self.passwd)
        #print publish_date
        for i in publish_date:
            print "第六步校验prodviewdb.products_core_search的publish_date为:%s" % self.publish_date_finally
            self.assertEqual(i,publish_date_ProductDB)  

            
    def get_xml_get_publish_date_from_frontend(self,product_id_list):
        keyword=u"股市制胜技法"
        sss=urllib.quote(keyword.encode("gbk"))
        #print sss
        debug_url="http://search.dangdang.com/?key=%s&category_debug=1" % sss
        search_contents=urllib2.urlopen(debug_url).read()        
        search_contents=search_contents.decode("gbk").encode("utf8")
        
        #因为后台xml地址所在的内容并不是真实的xml格式，所以现在还不能用beautifulsoup来解决  
        result=re.search(r"mix:<a href='(.*)'",search_contents)                      
        xml_url=result.groups(1)[0]
        #print "后台xml url的地址是:%s" % xml_url    
        
        c=urllib2.urlopen(xml_url).read()           
        format_c=ET.tostring(ET.parse(BytesIO(c)), encoding="utf-8")
        root=ElementTree.fromstring(format_c)
        x=root.getiterator("Product")
        for i in x:
            if i.find("product_id").text==product_id_list[0]:
                return i.find("publish_date").text

            
    def test_011_product_id_is_8712729_publish_date_is_2037_02_06(self):
        """股市制胜技法 该产品在前台显示的时间是2037-02-06"""
        print "*"*50
        print "test_011_product_id_is_8712729_publish_date_is_2037_02_06"
        #11111
        """       
        product_id_list=self.first_setup_get_product_id_list()
        """
        product_id_list=["8712729"]
        #product_id_list=["20351581"]
        
        #设置prodviewdb.publish_date的列publish_date为某一个值，然后检验product_id_list中的第一个产品id的publish_date为这个值，以确认更新mysql成功
        #222222
        publish_date_prodviewdb='1979-01-01 00:00:00'
        self.second_setup_update_publish_date_to_prodviewdb(product_id_list,publish_date_prodviewdb)          
        #设置ProductDB.Products_Core的列publish_date为NULL，然后检验product_id_list中的第一个产品id的publish_date为NULL，以确认更新mysql成功
        #333333
        
        publish_date_ProductDB=self.publish_date_small
        #publish_date_ProductDB="2010-07-29 14:29:48"
        self.third_setup_update_publish_date_to_ProductDB(product_id_list, publish_date_ProductDB)     
        #更新ProductDB.Products_Core的last_changed_date，并且校验该值跟输入的一致性
        #4444444
        
        last_changed_date="2013-07-29 14:29:48"
        process_last_date="2013-07-28 14:29:48"
                
        self.four_setup_update_last_changed_date_ProductDB(last_changed_date,product_id_list)       
        #更新prodviewdb.process_status的process_last_date，并且校验该值跟输入的一致性
        #5555555
        self.five_setup_update_process_last_date_prodviewdb(process_last_date,product_id_list)   
        #wait for ProductCoreSync
        while True:
            if self.check_sync_work_over():
                break
            else:
                sleep(10)
                continue 
        #publish_date of prodviewdb.products_core_search should not be changed
        publish_date=self.get_publish_date_all(product_id_list,self.db_search,"products_core_search",self.host_search,self.user,self.passwd)
        #print publish_date
        for i in publish_date:
            print "第六步校验prodviewdb.products_core_search的publish_date为:%s" % self.publish_date_finally
            self.assertEqual(i,self.publish_date_finally)
            
        while True:    
            publish_date_from_frontend=self.get_xml_get_publish_date_from_frontend(product_id_list)
            if publish_date_from_frontend==self.publish_date_finally:
                self.assertTrue(1==1)
                break
            else:
                sleep(10)
                continue
            
    
        
if __name__ == "__main__":
    unittest.main()   


    










