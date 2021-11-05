import json

from deepdiff import DeepDiff

# 接口返回的结构体中有值发生了改变，通过values_changed标识出来了
# 明确指出具体哪个字段的值发生改变了，如root['slideshow']['author']。
# 改变具体的内容，如实际返回值为Yours Truly，而预期值为Yours。

a = {'Object': {
    'code': '0',
    'message': 'success'
},
    'code': 1,
    'message': 'success'
}

b = {'Object':
    {
        'message': 'success',
        'code': '0'
    },
    'message': 'success'
}

print(DeepDiff(a, b, ignore_order=True))

# if 'dictionary_item_removed' in DeepDiff(a, b, ignore_order=True):
#     print('yes')
#
# print(type(b))
# dumps_b = json.dumps(b)
# print(dumps_b)
# print(type(dumps_b))
