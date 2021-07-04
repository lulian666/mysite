import json

import requests

url = "http://orange-match-beta.staging.codefuture.top/1.0/im/message/send"

payload = {'type': 'text', 'conversationId': '60bd98efa320940011977bb3'}
headers = {
    'x-jike-access-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiazNUZ0F6QXI3UzNtZ1BWekVUYXZybXh1S2c5TXRhYkxnRFNsbVhqOG5ySzMzdG5CY0EzZDM5K0NGZzJNK2FTdmZtYVA0UEdQbDZ3YlBnQ2Q2WlJoajRMakcwaDJTS25ENUJ2U05BZjVhcVl6MTZMODVaQjNselExQ1RHa1cyaXFOWFM3YzRNa0FrcUtuS0RreXFoUmZ3MVNrdlA1RkU2N1pUNmtPNFwvZjdodURlOFwvbWM4cDZKZUpLMmxVSmhZV3VIZnNNajI1Nkh6OVBsekkyN3BwMGFKSGNQS0NnOVVsTmdBdjh3T0R3WUNlWGFqSGFkbm55cFBibzQ3QkN5UXAydHJySnB5QnlTMzFTRVIwS0xjVkMreFMyUUNmZVwvOTRUN29SdEZyTTM0djd3NzJ0SUtVSXBwTklGZlRDNDVpZzFcL2ZDTHVURWNsQ0tKUTBXME9MdHNpdlBBK1diYmJaRGZaTmdZSEViQVJqQUtZWG4rUGlGY1hVR2QwSU1qbWtyOEVRNW1lOWJudk8zeE50Yzg1b29vRVIwc1JDWWFUdXoxVlYzR3BYaHlcL2FnPSIsInYiOjMsIml2IjoiVWY0MjJIZnlDYWRZV3VPUEZTRFFUUT09IiwiaWF0IjoxNjI1MTQxMzA5LjM4NH0.HUq3v1HYrne__L4Xi3vTWNxM41I96HSZzF7JhQR6ahI',
    'x-jike-device-id': '3272A7CD-872B-4DA1-B967-CECB5D908A26',
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

print(response.status_code, response.text)
