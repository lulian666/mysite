import json

import requests

url = "http://orange-match-beta.staging.codefuture.top/1.0/profile/update"

payload = {'screenName': '7001', 'height': '166', 'avatarFile': '[]', 'sportHobbies': '["足球"]', 'visitedCities': '["新德里"]', 'favMovies': '["闪灵"]', 'pet': '', 'purpose': '[]', 'questionId': '', 'answer': '', 'selfIntroduce': 'hh', 'aboutme': '我是一个没有感情的测试号', 'universityId': '5df8db6c9c6d0a4873889bc3', 'industry': '互联网', 'job': '产品', 'company': '三一重工', 'residence': '', 'hometown': '{"province":"安徽","city":"安庆"}', 'wechat': '3432653212', 'interestedEvents': '[]', 'socialActivities': '["打王者、吃鸡"]', 'name': '7001', 'photos': '[]', 'photoIds': '[]', 'lonelyTag': '5eaad0d19edf381521a76aaf', 'outlooksOnLove': '["5eb281255cec6c8287024e4b","5eb281255cec6c8287024e50","5eb281255cec6c8287024e55"]', 'title': {'province': '安徽', 'city': '安庆', 'interestedEvent': '', 'file': '', 'prefix': '', 'suffix': ''}, 'entertainment': ''}
headers = {
    'x-jike-access-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiMU1WbnZsVG9EN2tHN1BrS3MyTjI4Q25yUmR0SFFQa2x3UnhTSDNPVGxubnBlMnJRRXFEQVNYZ1ZISDVTc3hSSXJvRitva0h2NHBrVEt1TUNxTTdGdGE0aENVUU9qbGg3NUN1dVlKMWt4VTJBY1g1WUFRblwvMk5XcWxsNUhIeDhVNVFlXC9lOG9jZ2lwWDlmWlBEMGUrUkdNMUVVVklBVlZSRzdwdTQwMjR2ZXlhdW9iTjBuakxBNFwvbmhCMnYxU2NkQUcydDBBdUFGSDdpcTFTaXQrazRcLzNwdG5mVXM2b2VpdXYzOEdwbHo3MjZOb0JCY0E1K2xXNExTb0RVM3dBSERXQld4c3huUFpvbnFYWUFVSmFZSytUbjZvTXREdVBWYnBNZFNNQkdCUGdLVEV3VVg5SDJLZUh2VDNVQnN5NWV3aFJXcEIzV3lzaURaNzlFZWVyNUF5ejM5WHFUTHhxU2lyYjNFeThSZGwzMkR6RWEydUJyRWVmWVZCNE1aSUUxXC9hR2lpOUxBN3BWR0lxUVIxSk1peXE4YnRkaE94dE82TXl3NHlaQ1RGQVVNPSIsInYiOjMsIml2IjoidkN4blhsRVl6UlpaRng0OURmV21rdz09IiwiaWF0IjoxNjI1MjA1MjYwLjE1fQ.hvPcOOiIF8iVfXPWXziz_VzbVA8cZTSbV54IQ6MVGJo',
    'x-jike-device-id': '3272A7CD-872B-4DA1-B967-CECB5D908A26'
}
print(json.dumps(payload))
response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

print(response.status_code, response.text)
