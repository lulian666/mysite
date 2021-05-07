# coding:utf-8
import os

import requests
import json

from apitest.common.read_config import Read_config


class Refresh_token:
    def refresh(self):
        #refresh的url：
        #https://bitter.orangelovely.com/app_auth_tokens.refresh
        #post
        root = os.path.abspath('.') #获取当前工作目录路径
        filepath = os.path.join(root, 'apitest/config/header_kuainiao.json')
        with open(filepath, 'r', encoding='utf8')as fp:
            header = json.load(fp)
        fp.close()
        # header = {
        #               "content-type": "application/json",
        #               "authority": "commerce.codefuture.top",
        #               "app-version": "2.3.0",
        #               "accept-language": "zh-cn",
        #               "x-jike-client-type": "KEYBOARD",
        #               "accept-encoding": "deflat",
        #               "accept": "application/json, text/plain, */*",
        #               "user-agent": "Zboard/166 CFNetwork/1128.0.1 Darwin/19.6.0",
        #               "content-length": "98",
        #               "x-jike-access-token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiOUthQ1YwMXlHNk1RNnU5bTFRMFNUWGdMZ282VHIrTmdkTVdIcmhscjJYM2pvR3grSUQxMnVhRnVjSjE4ckZ4WEh2RnNjWk12SUpqd25ad2lCekZZUmhMclVlelBpclpIYlpqWVVHMVNzT0VrK1dGSnpJRkc0N1ZtdjFOUzhSdUdya2tGdWk4d1Q1aXp1S2Z1SWNGVFg1QUZoRklyNDhIM241bFJuVlZ5YUtJWTl0VTVRYzgrR3diWFIxV3JZVHBHOG5WSFJLVHFIZ0tVZlJsY2pQbktcL2hqOWJ1RVZjdFRWS1Y3UWhsMWtKQUpJSnlxa2ZCK1NZaTdRdE5SdXRUWGU1UnFSU3hOWmtBVldjdEF5eVIrZlwvV3d5SWNpZWRLTW1cL1ppMWZxaWZSeU9IeU1Ra05IVzJIQ2liT21VU3J4TFNUU0R5WGtQOEU3cThndlUyRE5xQ0o2RVpzUzAzaUliMGlhWGUwTFF6N3o0PSIsInYiOjMsIml2IjoiTFwvYWlvMDlaN1A3Mk9SWUNObmlaOXc9PSIsImlhdCI6MTYwMjUwMjAxOS4wMjd9.0Vqf5dAs7TC-GVLrAcVD2GGk0r5D1PGPSRHBayefEWY",
        #               "x-jike-refresh-token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiY1h3R0pzNnZHNmRETVVhbHBxUnNBXC9kNDBpWjVHQ001bjZUMDN4V1VDQnVTQjBXenM4RmF5WDdaRGl1ZFZDOW85K1B1OHh5K2JPOWZzSm1rY0tvclRZNUl2eFB0amE0NWVxakVnbVlSaHFYZGV0MThkZStMbldHMmpjV0xOT3l4Tkp0Y3VcL3NYcGMwaU1JOWJwSU9VQ0o1U3ExZk9oeWlMYzhjSkFFNTVIZ1ZkYlE1K1ZQM3NwaUV2OGY1elpIekUiLCJ2IjozLCJpdiI6IjAycFJCU084andGRVJibSt0Y2orXC9BPT0iLCJpYXQiOjE2MDI1MDAxOTQuMTQ5fQ.HNUg7vsAXrAgyztqi0sGprn63KWqzdIAX8g1G7iCIN0"
        #         }

        # url = 'https://commerce.codefuture.top/app_auth_tokens.refresh'
        url = Read_config().get_value('REQUEST','host')+'/app_auth_tokens.refresh'
        # print(url)

        result = requests.post(url, headers=header, json={})
        print('刷新token成功了吗？',result.status_code)
        response_body = result.json()
        # print(response_body)
        access_token = response_body['x-jike-access-token']
        refresh_token = response_body['x-jike-refresh-token']

        header["x-jike-access-token"] = access_token
        header["x-jike-refresh-token"] = refresh_token
        # print(access_token)
        # print(refresh_token)

        # root = os.path.abspath('.') #获取当前工作目录路径
        # filepath = os.path.join(root, 'apitest/config/header_kuainiao.json')
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(header, f)
        f.close()
        print('刷新了token')
        return