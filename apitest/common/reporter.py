# coding:utf-8
import time, os


class Template_mixin(object):
    """html报告"""
    HTML_TMPL = r"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>自动化测试报告</title>
            <link href="http://libs.baidu.com/bootstrap/3.0.3/css/bootstrap.min.css" rel="stylesheet">
            <h1 style="font-family: Microsoft YaHei">接口自动化测试报告</h1>
            <p class='attribute' style="font-size:30px;color:red"><strong>测试结果 : </strong> %(value)s</p>
            <style type="text/css" media="screen">
        body  { font-family: Microsoft YaHei,Tahoma,arial,helvetica,sans-serif;padding: 20px;}
        </style>
        </head>
        <body>
            <table id='result_table_fail' class="table table-condensed table-bordered table-hover">
                <colgroup>
                    <col align='left' />
                    <col align='right' />
                    <col align='right' />
                        <col align='right' />
                    </colgroup>
                    <tr id='header_row' class="text-center success" style="font-weight: bold;font-size: 14px;">
                        <th>测试时间</th>
                        <th>测试接口</th>
                        <th>接口方法</th>
                        <th>url参数</th>
                        <th>body内容</th>
                        <th >预期状态码</th>
                        <th>测试结果</th>
                    <th>实际状态码</th>
                    <th>返回结果</th>
                    <th>备注</th>
                </tr>
                %(table_tr)s
            </table>
            <table id='result_table_succ' class="table table-condensed table-bordered table-hover">
                <colgroup>
                    <col align='left' />
                    <col align='right' />
                    <col align='right' />
                    <col align='right' />
                </colgroup>
                <tr id='header_row' class="text-center success" style="font-weight: bold;font-size: 14px;">
                    <th>测试时间</th>
                    <th>测试接口</th>
                    <th>接口方法</th>
                    <th>url参数</th>
                    <th>body内容</th>
                    <th>预期状态码</th>
                    <th>测试结果</th>
                    <th>实际状态码</th>
                </tr>
                %(table_tr2)s
            </table>
        </body>
        </html>"""

    TABLE_TMPL_FAIL = """
        <tr class='failClass warning'>
            <td>%(runtime)s</td>
            <td>%(interface)s</td>
            <td>%(method)s</td>
            <td>%(parameters)s</td>
            <td>%(body)s</td>
            <td>%(expectcode)s</td>
            <td style="background-color:red">%(testresult)s</td>
            <td>%(testcode)s</td>
            <td>%(resultbody)s</td>
            <td>%(btw)s</td>
        </tr>"""

    TABLE_TMPL_SUCC = """
            <tr class='failClass warning'>
                <td>%(runtime)s</td>
                <td>%(interface)s</td>
                <td>%(method)s</td>
                <td>%(parameters)s</td>
                <td>%(body)s</td>
                <td>%(expectcode)s</td>
                <td>%(testresult)s</td>
                <td>%(testcode)s</td>
            </tr>"""


if __name__ == '__main__':
    #下面的都乱写的，应该已经不适用了，因为html有多次改动（不过反正也用不着这部分
    table_tr0 = ''
    numfail = 1
    numsucc = 9
    html = Template_mixin()

    table_td = html.TABLE_TMPL_FAIL % dict(version='3.8.8', step='输入正确的用户名，密码进行登录', runresult='登录成功',
                                           runtime=time.strftime('%Y-%m-%d %H:%M:%S'), )
    table_tr0 += table_td
    total_str = '共 %s，通过 %s，失败 %s' % (numfail + numsucc, numsucc, numfail)
    output = html.HTML_TMPL % dict(value=total_str, table_tr=table_tr0, )

    # 生成html报告
    filename = '{date}_TestReport.html'.format(date=time.strftime('%Y%m%d'))

    print(filename)
    # 获取report的路径
    dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '../report')
    filename = os.path.join(dir, filename)

    with open(filename, 'wb') as f:
        f.write(output.encode('utf8'))