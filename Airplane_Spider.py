# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
import re
from prettytable import PrettyTable
import string
import urllib.request
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import os



#在此设置需要查取得日期
ap_date=["2019-01-03","2019-01-04"]
#在此设置出发、到达城市 需要从携程查看相应城市代码
depart_city="SHA"
arrive_city="LHW"
#在此设置机票阈值
expect_price=800

#以下为邮箱设置
from_addr = '*****@qq.com'
password = '********'
to_addr = '*******@hotmail.com'
cc_addr = '*******@qq.com'
smtp_server = 'smtp.qq.com'

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def send_mail(data_html):

    msg = MIMEText(data_html, 'html', 'utf-8')
    msg['From'] = _format_addr('发件人:<%s>' % from_addr)
    msg['To'] = _format_addr('<%s>' % to_addr)
    msg['Subject'] = Header('抢购机票啦！', 'utf-8').encode()
    msg['Cc'] = _format_addr('<%s>' % cc_addr)

    server = smtplib.SMTP(smtp_server,587)
    server.set_debuglevel(1)
    server.starttls()
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr,cc_addr], msg.as_string())
    server.quit()



#options = webdriver.ChromeOptions()
#options.add_argument('--headless')#
#options.add_argument('--no-sandbox') 
#options.add_argument('--disable-gpu')
#options.add_argument('--disable-dev-shm-usage')
#browser = webdriver.Chrome(chrome_options=options)


browser=webdriver.Chrome()

airplane_table = PrettyTable(["航空公司", "出发地", "到达地", "出发时间", "到达时间", "价格"])
for yd_date in range(len(ap_date)):
    print(ap_date[yd_date])
    airplane_table.add_row(['----------------','--------------',ap_date[yd_date],'-----------','-----------','-----------'])
    browser.get("http://flights.ctrip.com/booking/"+depart_city+"-"+arrive_city+"-day-1.html?DDate1="+ap_date[yd_date])
    element = browser.find_elements("css selector", ".search_table_header")

    for i in range(len(element)):
        plane_data_temp=element[i].text
        plane_data=plane_data_temp.split()

        plane_al=plane_data[0]
        plane_dt=plane_data[3]
        plane_dpbn=plane_data[4]
        plane_at=plane_data[5]
        plane_apbn=plane_data[6]
        plane_lp=re.sub("\D", "", str(plane_data[9]))
        try:
            plane_lp_int=int(plane_lp)
        except ValueError:
            pass
        airline_al=plane_al[0:4]
        if plane_lp_int<expect_price:
            airplane_table.add_row([plane_al,plane_dpbn,plane_apbn,plane_dt,plane_at,plane_lp])
        print(plane_data)
    time.sleep(10)#此处不建议注释 以防被封


data_html = airplane_table.get_html_string()
send_mail(data_html)
browser.close()
os.system('taskkill /im chromedriver.exe /F')
