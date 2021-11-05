import json
import math

import requests
from requests import Request

url = "http://orange-match-beta.staging.codefuture.top/1.0/profile/update"

payload = {'screenName': '7001', 'height': '166', 'avatarFile': '[]', 'sportHobbies': '["足球"]', 'visitedCities': '["新德里"]', 'favMovies': '["闪灵"]', 'pet': '', 'purpose': '[]', 'questionId': '', 'answer': '', 'selfIntroduce': 'hh', 'aboutme': '我是一个没有感情的测试号', 'universityId': '5df8db6c9c6d0a4873889bc3', 'industry': '互联网', 'job': '产品', 'company': '三一重工', 'residence': '', 'hometown': '{"province":"安徽","city":"安庆"}', 'wechat': '3432653212', 'interestedEvents': '[]', 'socialActivities': '["打王者、吃鸡"]', 'name': '7001', 'photos': '[]', 'photoIds': '[]', 'lonelyTag': '5eaad0d19edf381521a76aaf', 'outlooksOnLove': '["5eb281255cec6c8287024e4b","5eb281255cec6c8287024e50","5eb281255cec6c8287024e55"]', 'title': {'province': '安徽', 'city': '安庆', 'interestedEvent': '', 'file': '', 'prefix': '', 'suffix': ''}, 'entertainment': ''}
headers = {
    'x-jike-access-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiMU1WbnZsVG9EN2tHN1BrS3MyTjI4Q25yUmR0SFFQa2x3UnhTSDNPVGxubnBlMnJRRXFEQVNYZ1ZISDVTc3hSSXJvRitva0h2NHBrVEt1TUNxTTdGdGE0aENVUU9qbGg3NUN1dVlKMWt4VTJBY1g1WUFRblwvMk5XcWxsNUhIeDhVNVFlXC9lOG9jZ2lwWDlmWlBEMGUrUkdNMUVVVklBVlZSRzdwdTQwMjR2ZXlhdW9iTjBuakxBNFwvbmhCMnYxU2NkQUcydDBBdUFGSDdpcTFTaXQrazRcLzNwdG5mVXM2b2VpdXYzOEdwbHo3MjZOb0JCY0E1K2xXNExTb0RVM3dBSERXQld4c3huUFpvbnFYWUFVSmFZSytUbjZvTXREdVBWYnBNZFNNQkdCUGdLVEV3VVg5SDJLZUh2VDNVQnN5NWV3aFJXcEIzV3lzaURaNzlFZWVyNUF5ejM5WHFUTHhxU2lyYjNFeThSZGwzMkR6RWEydUJyRWVmWVZCNE1aSUUxXC9hR2lpOUxBN3BWR0lxUVIxSk1peXE4YnRkaE94dE82TXl3NHlaQ1RGQVVNPSIsInYiOjMsIml2IjoidkN4blhsRVl6UlpaRng0OURmV21rdz09IiwiaWF0IjoxNjI1MjA1MjYwLjE1fQ.hvPcOOiIF8iVfXPWXziz_VzbVA8cZTSbV54IQ6MVGJo',
    'x-jike-device-id': '43a113a2-7433-4c8a-80a2-66de744dad67',
    'x-jike-refresh-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoic3JxdXV5U0ZqeHdlRHZwNEVvRmp2QlEzTVRSNU4xUURKOWtENHBoazR0akxUbW9iOG1RUkQ2cnRLcHZ5K3lVb3g5UjI1b2VqUEZcL3Z0ZG5xOThQb2E2VHdYdHVneDJJRjZuMjBBR3ROSE1PUWRrdGZrdUcya2JITTBHSHZYeGcrdmlzT0pDYUJTaTlJTFwvMXZnMmRES21FRXh6N2Y5N1grZ0ZJU0J6b3JHSGFCRFdGS0k1NlI4VjgzajdHM2FBZTZablllUkVWYkpxMFZQVVBsUzUxZExWT21IM1Jiem9GakNmSkVVTXNWWm1kbmNyMGc5RjlUcTlaVlVwdmJhSVBvIiwidiI6MywiaXYiOiJmUXg4RURaS1ZkR1NLRlwvNDYwTElWdz09IiwiaWF0IjoxNjMwMjI4MDc3LjcwMn0.GYjeL_QB1Bl3HLknpUAvsEEcj8oNzXpw_YUUtazUIWg'
}

# cookies = {'test': 'test'}


# print(json.dumps(payload))

# s = requests.Session()
# req = Request('POST', url, data=json.dumps(payload), headers=headers)
# # prepped = req.prepare()
# prepped = s.prepare_request(req)
# response = s.send(prepped)


# def refresh_token(resp, *args, **kwargs):
#     print(resp.url)
#     print(resp.status_code)
#     if resp.status_code == 401:
#         refresh_url = 'http://orange-match-beta.staging.codefuture.top' + '/app_auth_tokens.refresh'
#         refresh_resp = requests.post(refresh_url, headers=resp.request.headers, json={})
#         resp.request.headers['x-jike-access-token'] = refresh_resp.json()['x-jike-access-token']
#         resp.request.headers['x-jike-refresh-token'] = refresh_resp.json()['x-jike-refresh-token']
#         # new_resp = requests.request(method=resp.request.method, url=resp.request.url, headers=headers, data=resp.request.content)
#         new_resp = requests.Session().send(resp.request)
#         return new_resp
#
#
# response = requests.request("POST", url, headers=headers, data=json.dumps(payload), hooks=dict(response=refresh_token))

# print(response.status_code, response.text)
# print(response.history)
# print(response.status_code == requests.codes.ok)


# def print_url(r, *args, **kwargs):
#     print(r.url)
#
#
# def print_time(r, *args, **kwargs):
#     print(r.elapsed)


# r = requests.get('http://httpbin.org/get', hooks=dict(response=print_time))
# r.raise_for_status()
# print(r.elapsed)
# print(r.reason)
'''
list1 = [1, 2, 3, 4, 5]
list2 = [a ** 2 for a in list1 if a ** 2 > 10]
# 或者
# list2 = [a * a for a in list1 if a * a > 10]
print(list2)
'''
# print(list3)
# print(list4)

# list2 = [math.pow(a, 2) for a in list1 if math.pow(a, 2) > 10]


# def gen():
#     yield 'hi'
#     yield 'there'
#
#
# requests.post('http://some.url/chunked', data=gen())
#
# # print(r.content)

# def test(a, **kwargs):
#     print(a)
#     if 'test' in kwargs:
#         print(kwargs['test'])
#     else:
#         print(kwargs)
#
#
# test('a', json_path='json_path')
# # test('b', 'b')
# test('c')


# list1 = [1, 2, 3, 4, 5]
# a = (item+1 for item in list1)
#
# print(a)

# url = 'http://httpbin.org/post'
# files = {'file': open('report.xls', 'rb')}
#
# r = requests.post(url, files=files)
# r.text



# resp1 = {
#     "data": [
#         {
#             "id": "abcdefg",
#             "interval": "month",
#             "intervalUnit": 6,
#             "perUnitPrice": 5000,
#             "perUnitPriceBeforePromotion": 7800,
#             "percentOff": 30,
#             "description": "最受欢迎",
#             "default": True,
#             "iapId": "com.orange.6month"
#         },
#         {
#             "id": "abcde",
#             "interval": "month",
#             "intervalUnit": 1,
#             "perUnitPrice": 7800,
#             "perUnitPriceBeforePromotion": 7800,
#             "percentOff": 0,
#             "description": "",
#             "default": False,
#             "iapId": "com.orange.1month"
#         },
#         {
#             "id": "abcd",
#             "interval": "month",
#             "intervalUnit": 12,
#             "perUnitPrice": 3200,
#             "perUnitPriceBeforePromotion": 7800,
#             "percentOff": 70,
#             "description": "最实惠",
#             "default": False,
#             "iapId": "com.orange.12months"
#         }
#     ]
# }
#
# resp2 = {
#     "data": [
#         {
#             "id": "612645ed24b46a09b8225024",
#             "interval": 1,
#             "intervalUnit": "month",
#             "perUnitPrice": 10000,
#             "perUnitPriceBeforePromotion": 10000,
#             "percentOff": 0,
#             "default": False,
#             "iapId": "com.orangelovely.subscription.1month",
#             "totalPrice": 10000
#         },
#         {
#             "id": "61264627dedd2c0ffcb7e3c7",
#             "interval": 6,
#             "intervalUnit": "month",
#             "perUnitPrice": 5000,
#             "perUnitPriceBeforePromotion": 10000,
#             "percentOff": 50,
#             "description": "最受欢迎",
#             "default": True,
#             "iapId": "com.orangelovely.subscription.6months",
#             "totalPrice": 30000
#         },
#         {
#             "id": "6126477616400f327f445766",
#             "interval": 12,
#             "intervalUnit": "month",
#             "perUnitPrice": 3000,
#             "perUnitPriceBeforePromotion": 10000,
#             "percentOff": 70,
#             "description": "最实惠",
#             "default": True,
#             "iapId": "com.orangelovely.subscription.12months",
#             "totalPrice": 36000
#         }
#     ]
# }
#
# diff = deepdiff.DeepDiff(resp1, resp2, ignore_order=True)
# print(diff)
# if 'type_changes' in diff:
#     print(diff['type_changes'])
# if 'dictionary_item_removed' in diff:
#     print(diff['dictionary_item_removed'])

import json
import requests

# r = requests.get('http://httpbin.org/stream/20', stream=True)

# if r.encoding is None:
#     r.encoding = 'utf-8'
#
# for line in r.iter_lines(decode_unicode=True):
#     if line:
#         print(json.loads(line))
# lines = r.iter_lines()
# 保存第一行以供后面使用，或者直接跳过

# first_line = next(lines)
#
# for line in lines:
#     print(line)


# for line in r.iter_lines(decode_unicode=True):
#     if line:
#         data = json.loads(line)
#         print(data['id'])

# proxies = {
#     "http": "http://10.0.98.26:8889",
#     "https": "http://10.0.98.26:8889",
# }
# proxies = {
#     'http': 'socks5://user:pass@host:port',
#     'https': 'socks5://user:pass@host:port'
# }

# requests.get("http://example.org", proxies=proxies)
# r = requests.get('https://api.github.com/repos/requests/requests/git/commits/a050faf084662f3a352dd1a941f2c7c9f886d4ad')
# verbs = requests.options(r.url)
verbs = requests.options('http://a-good-website.com/api/cats')
print(verbs.headers['allow'])





