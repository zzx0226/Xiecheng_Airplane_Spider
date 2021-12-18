# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from prettytable import PrettyTable
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import os
#在此设置需要查取得日期
ap_date = ["2022-01-09", "2022-01-10"]
#在此设置出发、到达城市 需要从携程查看相应城市代码
depart_city = "SHA"
arrive_city = "BJS"
#在此设置机票阈值
expect_price = 1000

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

    server = smtplib.SMTP(smtp_server, 587)
    server.set_debuglevel(1)
    server.starttls()
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr, cc_addr], msg.as_string())
    server.quit()


options = webdriver.EdgeOptions()
options.add_argument('--headless')  #
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
driverfile_path = 'edgedriver_linux64/msedgedriver'  #这里填edgedriver的地址
browser = webdriver.Edge(executable_path=driverfile_path, options=options)

js_down = "var q=document.documentElement.scrollTop=10000"
js_top = "var q=document.documentElement.scrollTop=0"
airplane_table = PrettyTable(["航空公司", "出发地", "到达地", "出发时间", "到达时间", "价格"])
for yd_date in ap_date:
    print(f'{yd_date},expect price 800')
    airplane_table.add_row(['----------------', '--------------', yd_date, '-----------', '-----------', '-----------'])

    browser.get(f"https://flights.ctrip.com/online/list/oneway-{depart_city}-{arrive_city}?_=1&depdate={yd_date}")

    browser.execute_script(js_down)  #滚动网页 使得数据加载完毕
    browser.implicitly_wait(5)
    browser.execute_script(js_down)
    browser.implicitly_wait(2)
    browser.execute_script(js_top)
    browser.implicitly_wait(3)
    browser.execute_script(js_down)

    flight_detials = browser.find_elements(By.CLASS_NAME, 'flight-detail')
    flight_prices = browser.find_elements(By.CLASS_NAME, 'flight-operate')
    flight_airlines = browser.find_elements(By.CLASS_NAME, 'flight-airline')

    for i, (flight_detial, flight_price, flight_airline) in enumerate(zip(flight_detials, flight_prices, flight_airlines)):
        flight_detial_text = flight_detial.get_attribute('innerText')
        flight_airline = flight_airline.get_attribute('innerText').split('\n')[0]
        try:  #经停航班会有更多的返回值 不考虑经停航班
            plane_dt, plane_dl, plane_at, plane_al = flight_detial_text.split("\n")
        except:
            continue
        Price = flight_price.get_attribute('innerText').split('\n')[0][1:-1]
        if int(Price) < expect_price:
            airplane_table.add_row([flight_airline, plane_dl, plane_al, plane_dt, plane_at, Price])
    time.sleep(10)
print(airplane_table)

data_html = airplane_table.get_html_string()
# send_mail(data_html)
browser.close()
# os.system('taskkill /im edgedriver.exe /F')
