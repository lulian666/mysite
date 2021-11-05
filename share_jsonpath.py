import jsonpath

resp1 = {
    "data": [
        {
            "id": "abcdefg",
            "interval": "month",
            "intervalUnit": 6,
            "perUnitPrice": 5000,
            "perUnitPriceBeforePromotion": 7800,
            "percentOff": 30,
            "description": "最受欢迎",
            "default": True,
            "iapId": "com.orange.6month"
        },
        {
            "id": "abcde",
            "interval": "month",
            "intervalUnit": 1,
            "perUnitPrice": 7800,
            "perUnitPriceBeforePromotion": 7800,
            "percentOff": 0,
            "description": "",
            "default": False,
            "iapId": "com.orange.1month"
        },
        {
            "id": "abcd",
            "interval": "month",
            "intervalUnit": 12,
            "perUnitPrice": 3200,
            "perUnitPriceBeforePromotion": 7800,
            "percentOff": 70,
            "description": "最实惠",
            "default": False,
            "iapId": "com.orange.12months"
        }
    ]
}
# 当找到搜索内容时返回 list，当没有搜索到时返回 False
# query_string = '$.data[0].id'
# query_string = '$.data[0]'
query_string = '$.data[0].test'
result = jsonpath.jsonpath(resp1, query_string)
print(result)
print(type(result))
