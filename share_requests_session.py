import json

import requests


url = 'http://orange-match-beta.staging.codefuture.top/1.0/account/sms/getCode'
body = {'areaCode': '+86', 'mobilePhoneNumber': '14012347001'}
headers = {
    'x-jike-access-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiMU1WbnZsVG9EN2tHN1BrS3MyTjI4Q25yUmR0SFFQa2x3UnhTSDNPVGxubnBlMnJRRXFEQVNYZ1ZISDVTc3hSSXJvRitva0h2NHBrVEt1TUNxTTdGdGE0aENVUU9qbGg3NUN1dVlKMWt4VTJBY1g1WUFRblwvMk5XcWxsNUhIeDhVNVFlXC9lOG9jZ2lwWDlmWlBEMGUrUkdNMUVVVklBVlZSRzdwdTQwMjR2ZXlhdW9iTjBuakxBNFwvbmhCMnYxU2NkQUcydDBBdUFGSDdpcTFTaXQrazRcLzNwdG5mVXM2b2VpdXYzOEdwbHo3MjZOb0JCY0E1K2xXNExTb0RVM3dBSERXQld4c3huUFpvbnFYWUFVSmFZSytUbjZvTXREdVBWYnBNZFNNQkdCUGdLVEV3VVg5SDJLZUh2VDNVQnN5NWV3aFJXcEIzV3lzaURaNzlFZWVyNUF5ejM5WHFUTHhxU2lyYjNFeThSZGwzMkR6RWEydUJyRWVmWVZCNE1aSUUxXC9hR2lpOUxBN3BWR0lxUVIxSk1peXE4YnRkaE94dE82TXl3NHlaQ1RGQVVNPSIsInYiOjMsIml2IjoidkN4blhsRVl6UlpaRng0OURmV21rdz09IiwiaWF0IjoxNjI1MjA1MjYwLjE1fQ.hvPcOOiIF8iVfXPWXziz_VzbVA8cZTSbV54IQ6MVGJo',
    'x-jike-device-id': '43a113a2-7433-4c8a-80a2-66de744dad67',
    'Content-Type': 'application/json',
    'x-jike-refresh-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoic3JxdXV5U0ZqeHdlRHZwNEVvRmp2QlEzTVRSNU4xUURKOWtENHBoazR0akxUbW9iOG1RUkQ2cnRLcHZ5K3lVb3g5UjI1b2VqUEZcL3Z0ZG5xOThQb2E2VHdYdHVneDJJRjZuMjBBR3ROSE1PUWRrdGZrdUcya2JITTBHSHZYeGcrdmlzT0pDYUJTaTlJTFwvMXZnMmRES21FRXh6N2Y5N1grZ0ZJU0J6b3JHSGFCRFdGS0k1NlI4VjgzajdHM2FBZTZablllUkVWYkpxMFZQVVBsUzUxZExWT21IM1Jiem9GakNmSkVVTXNWWm1kbmNyMGc5RjlUcTlaVlVwdmJhSVBvIiwidiI6MywiaXYiOiJmUXg4RURaS1ZkR1NLRlwvNDYwTElWdz09IiwiaWF0IjoxNjMwMjI4MDc3LjcwMn0.GYjeL_QB1Bl3HLknpUAvsEEcj8oNzXpw_YUUtazUIWg'
}

url2 = 'https://httpbin.org/cookies'

s = requests.Session()
s.headers = headers

time_for_r1 = time_for_r2 = 0
# for i in range(0, 5):
#     r1 = s.post(url, data=json.dumps(body))
#     # r1 = s.get(url2, verify=False)
#     time = r1.elapsed
#     time_for_r1 += time.total_seconds()
#     print('r1:', r1.elapsed)
# print('r1总耗时', time_for_r1)
# print()

for i in range(0, 5):
    r2 = requests.post(url, headers=headers, data=json.dumps(body))
    # r2 = requests.get(url2, verify=False)
    time = r2.elapsed
    time_for_r2 += time.total_seconds()
    print('r2:', r2.elapsed)

print('r2总耗时', time_for_r2)
