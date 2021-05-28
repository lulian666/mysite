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

