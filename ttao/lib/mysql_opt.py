# -*- coding: utf-8 -*-
import pymysql

class MysqlOpt(object):
    def __init__(self,host,user,password):
        self.host = host
        self.user = user
        self.password = password

    def m_exect(self,sql,database=""):
        db = pymysql.connect(self.host,self.user,self.password,database)
        cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
        res =cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()
        return res

    def m_select(self,sql,database=""):
        db = pymysql.connect(self.host,self.user,self.password,database)
        cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(sql)
        res = cursor.fetchall()
        cursor.close()
        db.close()
        return res