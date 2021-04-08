# coding:utf-8
import os
import smtplib
import time
from email.mime.text import MIMEText
from email.header import Header

from email.mime.application import MIMEApplication  #主要类型的MIME消息对象应用
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import threading

from apitest.common.read_config import Read_config

localReadConfig = Read_config()
filename = '{date}_TestReport.html'.format(date=time.strftime('%Y%m%d%H'))
dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '../report')
filename = os.path.join(dir, filename)

class Email:
    def __init__(self,num_fail):

        global host, user, password, port, sender, title,receivers

        sender = localReadConfig.get_value('EMAIL','sender') # 发件人
        # receivers = ['lulian@iftech.io','zhouxin@iftech.io','songwei@iftech.io']  # 收件人
        receivers = ['lulian@iftech.io']  # 收件人
        # receivers = ['test@163.com','test@vip.qq.com']  # 接收多个邮件，可设置为你的QQ邮箱或者其他邮箱
        host = localReadConfig.get_value('EMAIL','mail_host')# 设置服务器
        port = localReadConfig.get_value('EMAIL','mail_port') # 设置服务器
        user = localReadConfig.get_value('EMAIL','mail_user')# QQ邮件登录名称
        password = localReadConfig.get_value('EMAIL','mail_pass')# QQ邮箱的授权码

        title = localReadConfig.get_value('EMAIL','subject')#邮件主题

        # 定义邮件主题
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if num_fail == 0:
            subject = '所有case测试通过'
        else:
            subject = '%s 条case测试未通过' %(num_fail)
        print(subject)

        self.subject = '接口测试报告：【' + subject + '】 ' + date
        self.msg = MIMEMultipart('related')
        self.msg.attach(MIMEText('如有修复/更新可以同步QA（如果打开附件发现没有格式，下载后再打开即可）', 'plain', 'utf-8'))


    def config_header(self):
        """
        defined emai l header include subject, sender and receiver
        :return:
        """
        self.msg['Subject'] = Header(self.subject)  # 邮件主题
        self.msg['From'] = Header(sender)  # 发件人
        self.msg['To'] = Header(str(";".join(receivers)))  # 收件人

    def config_content(self):
        """
        write the content of email
        :return:
        """
        self.config_file()

    def config_file(self):
        if self.check_file():
            print('附件：',filename)
            with open(filename, 'rb') as f:
                attach_files = MIMEApplication(f.read())
                attach_files.add_header('Content-Disposition', 'attachment', filename='{date}_TestReport.html'.format(date=time.strftime('%Y%m%d%H')))
                self.msg.attach(attach_files)


    def check_file(self):
        """
        check test report
        :return:
        """
        report_path = filename
        if os.path.isfile(report_path) and not os.stat(report_path) == 0:
            return True
        else:
            print('没找到附件')
            return False

    def send_email(self):
        """
        send email
        :return:
        """
        global smtp
        self.config_content()
        self.config_header()
        try:
            smtp = smtplib.SMTP_SSL(host,port)
            smtp.login(user, password)
            smtp.sendmail(sender, receivers, self.msg.as_string())
            print('发送成功')
        except Exception as ex:
            print('发送失败')
            print(str(ex))
            return "邮件发送失败"
        finally:
            smtp.quit()

class MyEmail:
    email = None
    mutex = threading.Lock()
    num_fail = 0

    def __init__(self,numfail):
        self.num_fail = numfail
        pass

    @staticmethod
    def get_email():

        if MyEmail.email is None:
            print('MyEmail.num_fail:',MyEmail.num_fail)
            MyEmail.mutex.acquire()
            MyEmail.email = Email(MyEmail.num_fail)
            MyEmail.email.send_email()

            MyEmail.mutex.release()
        return MyEmail.email


if __name__ == "__main__":
    email = MyEmail.get_email()
