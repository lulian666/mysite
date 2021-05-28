# coding:utf-8
import os
import smtplib
import time
from email.mime.text import MIMEText
from email.header import Header

from email.mime.application import MIMEApplication  # 主要类型的MIME消息对象应用
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import threading
from fnmatch import fnmatch
from os import listdir

from apitest.common.read_config import Read_config

localReadConfig = Read_config()
global host, user, password, port, sender, title, receivers


class Email:
    def __init__(self, num_fail):
        global host, user, password, port, sender, title, receivers
        sender = localReadConfig.get_value('EMAIL', 'sender')  # 发件人
        # receivers = ['lulian@iftech.io','zhouxin@iftech.io','songwei@iftech.io']  # 收件人
        receivers = ['lulian@iftech.io']  # 收件人
        # receivers = ['test@163.com','test@vip.qq.com']  # 接收多个邮件，可设置为你的QQ邮箱或者其他邮箱
        host = localReadConfig.get_value('EMAIL', 'mail_host')  # 设置服务器
        port = localReadConfig.get_value('EMAIL', 'mail_port')  # 设置服务器
        user = localReadConfig.get_value('EMAIL', 'mail_user')  # QQ邮件登录名称
        password = localReadConfig.get_value('EMAIL', 'mail_pass')  # QQ邮箱的授权码
        title = localReadConfig.get_value('EMAIL', 'subject')  # 邮件主题

        # 定义邮件主题
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if num_fail == 0:
            subject = '所有case测试通过'
        else:
            subject = '%s 条case测试未通过' % (num_fail)

        self.subject = '接口测试报告：【' + subject + '】 ' + date
        self.msg = MIMEMultipart('related')
        self.msg.attach(MIMEText('如有修复/更新可以同步QA（如果打开附件发现没有格式，下载后再打开即可）', 'plain', 'utf-8'))

    def config_header(self):
        """
        defined emai l header include subject, sender and receiver
        :return:
        """
        self.msg['Subject'] = Header(self.subject)
        self.msg['From'] = Header(sender)
        self.msg['To'] = Header(str(";".join(receivers)))

    def config_content(self):
        """
        write the content of email
        :return:
        """
        self.config_file()

    def config_file(self):
        if self.check_file():
            filename = self.check_file()
            print("附件：{filename}".format(filename=filename))
            with open(filename, 'rb') as f:
                attach_files = MIMEApplication(f.read())
                attach_files.add_header('Content-Disposition', 'attachment',
                                        filename='{date}_TestReport.html'.format(date=time.strftime('%Y%m%d%H')))
                self.msg.attach(attach_files)

    def check_file(self):
        """
        check test report
        :return:
        """
        root = os.path.abspath('.')
        filepath = os.path.join(root, 'apitest/templates/report')
        filetime = time.strftime('%Y%m%d%H%M')
        filename = [file for file in listdir(filepath) if fnmatch(file, '*' + filetime + '*')]
        filename = "".join(str(item) for item in filename)
        filename = os.path.join(filepath, filename)
        report_path = filename

        if os.path.isfile(report_path) and not os.stat(report_path) == 0:
            return filename
        else:
            print('没找到附件')
            print(report_path)
            return False

    def send_email(self):
        """
        send email
        :return:
        """
        print("sending email")
        self.config_content()
        self.config_header()
        try:
            smtp = smtplib.SMTP_SSL(host, port)
            smtp.login(user, password)
            smtp.sendmail(sender, receivers, self.msg.as_string())
            print('发送成功')
        except Exception as ex:
            print('发送失败')
            print(str(ex))
            return "邮件发送失败"
        finally:
            smtp.quit()

