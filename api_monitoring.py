#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging
import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time
import paramiko

def api_monitoring():
    url = "https://www.mulantools.top/Api/api_status"
    # 发送get请求
    try:
        r = requests.get(url)
        res = r.json()['params']
        if res == 'normal_operation':
            return True
        else:
            return False
    except:
        return False
def send_mail():
    # 第三方 SMTP 服务
    mail_host = "smtp.qq.com"  # 设置服务器
    mail_user = "发送邮件的邮箱地址"  # 用户名
    mail_pass = "口令"  # 口令

    sender = '发送邮件的邮箱地址'
    receivers = ['接收邮件的的邮箱地址1','接收邮件的邮箱地址2']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    message = MIMEText('api无法连接，请到服务器查看', 'plain', 'utf-8')
    message['From'] = Header("api监控程序", 'utf-8')
    message['To'] = Header("开发者", 'utf-8')

    subject = 'API无法连接'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        initLogging('info','邮件发送成功')

    except smtplib.SMTPException:
        initLogging('warning','无法发送邮件')


def remotConnect():
    # 服务器相关信息,下面输入你个人的用户名、密码、ip等信息
    ip = "服务器ip"
    port = 22
    user = "用户名"
    password = "密码"

    # 创建SSHClient 实例对象
    ssh = paramiko.SSHClient()
    # 调用方法，表示没有存储远程机器的公钥，允许访问
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接远程机器，地址，端口，用户名密码
    ssh.connect(ip, port, user, password, timeout=10)
    # 输入linux命令
    pkill_uwsgi = 'sudo pkill -f uwsgi -9'
    start_uwsgi = 'uwsgi --ini uwsgi.ini --daemonize /var/log/uwsgi.log'
    ssh.exec_command(pkill_uwsgi)
    ssh.connect(ip, port, user, password, timeout=10)
    ssh.exec_command(start_uwsgi)
    ssh.close()


def initLogging(rank, e):
    logging.basicConfig(filename='./' + __name__ + '.log',
                        format='[%(asctime)s-%(filename)s-%(levelname)s:%(message)s]', level=logging.DEBUG,
                        filemode='a', datefmt='%Y-%m-%d%I:%M:%S %p')
    if rank == 'info':
        logging.info(e)
    else:
        logging.warning(e)

if __name__ == '__main__':
    is_normal_operation = True
    while is_normal_operation == True:
        if api_monitoring():
            initLogging('info','连接正常')
            pass
        else:
            send_mail()
            initLogging('warning','连接异常')
            try:
                remotConnect()
            except:
                is_normal_operation = False
        time.sleep(60)
