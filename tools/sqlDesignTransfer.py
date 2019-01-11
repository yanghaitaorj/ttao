# coding:utf-8
from os import sys, path
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from lib.mysql_opt import MysqlOpt

class Sql_Transfer(object):
    def __init__(self,host,user,password):
        self.mo = MysqlOpt(host,user,password)
        self.sql_map = {}
        self.type_map = {
                        "varchar": "String",
                        "blob": "String",
                        "longblob": "String",
                        "datetime": "DateTime",
                        "timestamp": "DateTime",
                        "time": "DateTime",
                        "bigint": "BigInteger",
                        "smallint": "SmallInteger",
                        "tinyint": "SmallInteger",
                        "mediumtext": "Text",
                        "text": "Text",
                        "longtext": "Text",
                        "int": "Integer",
                        "double": "Float",
                        "char": "String",
                        "set": "Enum",
                        "enum": "Enum"
                        }

    def get_databasess(self,balck_list=[],white_list=[]):
        databases = self.mo.m_select(sql="show databases;",database="")
        for item in databases:
            database = item["Database"]
            if database not in balck_list and database in white_list:
                self.sql_map[database] = {}

    def get_tables(self,database):
        tables = self.mo.m_select(sql = "show tables;",database=database)
        for item in tables:
            table = item["Tables_in_"+database]
            self.sql_map[database][table] = {}

    def get_table_design(self,table,database):
        table_designs = self.mo.m_select(sql = "desc "+table,database=database)
        self.sql_map[database][table] = table_designs

    def get_all_designs(self,balck_list=[],white_list=[]):
        self.get_databasess(balck_list,white_list)
        for database in self.sql_map.keys():
            self.get_tables(database)
            for table in self.sql_map[database].keys():
                self.get_table_design(table,database)

    def type_transfer(self,i_type):
        if i_type in self.type_map.keys():   # 类型存在映射表中
            i_type = i_type.replace(i_type,self.type_map[i_type])+"()"
        elif "int" in i_type:
            old_type = i_type.split("(")[0]
            new_type = self.type_map[old_type]
            i_type = new_type+"()"
        elif "(" in i_type and i_type.split("(")[0] in self.type_map.keys(): # 类型有长度声明，提取类型字段，找到映射表映射value，并替换
            old_type = i_type.split("(")[0]
            new_type = self.type_map[old_type]
            i_type = i_type.replace(old_type,new_type)
        return i_type

    def transfer(self,dir_path,sql_design):
        for database in sql_design.keys():
            rst = ["from sqlalchemy.ext.declarative import declarative_base\n",
                    "from sqlalchemy import Column,Integer,String,BigInteger,DateTime,SmallInteger,Text,Enum\n",
                    "Base = declarative_base()\n"]
            for table in sql_design[database].keys():
                rst.append("\nclass %s(Base):\n" % table)
                rst.append("    "+'__tablename__ = "%s"\n' % table)
                for item in sql_design[database][table]:
                    s_type = self.type_transfer(item["Type"])
                    column = "    "+item["Field"] + " = Column(" + s_type + ")\n"
                    if item["Key"] == "PRI":
                        column = "    "+item["Field"] + " = Column(" + s_type + ", primary_key=True)\n"
                    rst.append(column)
            file_name = dir_path+"\%s.py" % database
            with open(file_name,"a+") as f:
                for line in rst:
                    f.write(line)

if __name__ == "__main__":
    host=""
    user=""
    password=""
    dir_path = ".\modules"
    st = Sql_Transfer(host,user,password)
    st.get_all_designs()
    st.transfer(dir_path,st.sql_map)