import sqlalchemy
from sqlalchemy import text
import urllib
import datetime
import config

#cn_string = 'Driver={ODBC Driver 17 for SQL Server};Server=tcp:dxcdb1.database.windows.net,1433;Database=dxc;Uid=dxcadmin@dxcdb1;Pwd=DXC@dmin;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
cn_string = config.CONNECTION_STRING
params = urllib.parse.quote_plus(cn_string)
engine = sqlalchemy.engine.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
engine.connect()# -*- coding: utf-8 -*-
    
def createAlert(phone, frequency, parameter, condition, value, email):
    print('Creating New Alert Record')
    query = """INSERT INTO dbo.alerts(mobilenumber, frequency, parameter, condition, value, datecreated, email) values  ('"""+str(phone)+"""','"""+str(frequency)+"""','"""+ str(parameter) +"""','"""+ str(condition) + """',"""+ str(value)+ """,'""" +str(datetime.datetime.now())+"""','"""+str(email)+"""')"""
    engine.execute(text(query).execution_options(autocommit=True))


