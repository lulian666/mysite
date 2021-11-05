"""
python 提供了一种精炼的写法，可以根据一份列表来制作另外一份
名为 python 的列表推导，也称 list comprehension
"""
# 用列表推导来取代 map 和 filter
a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
squares = [x**2 for x in a]
print(squares)
# >>> [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

# 如果要使用 map，那就要创建 lambda 函数，以便计算新列表中各个元素的值，这会使代码看起来有些乱
squares = map(lambda x: x ** 2, a)

# 假设我们只想计算哪些可以为 2 所整除的数，如果用列表推导做，只需要在循环后面添加条件表达式即可：
even_squares = [x**2 for x in a if x % 2 == 0]
print(even_squares)
# >>> [4, 16, 36, 64, 100]

# 用 filter 函数与 map 结合起来，也能达成同样的效果，但是代码会写得非常难懂：
alt = map(lambda x: x**2, filter(lambda x: x % 2 == 0, a))
assert even_squares == list(alt)

# 字典和集合也有列表类似的推导机制：
chile_ranks = {'ghost': 1, 'habanero': 2, 'cayenne': 3}
rank_dict = {rank: name for name, rank in chile_ranks.items()}
chile_len_set = {len(name) for name in rank_dict.values()}
print(rank_dict)
print(chile_len_set)
# >>> {1: 'ghost', 2: 'habanero', 3: 'cayenne'}
# >>> {8, 5, 7}

# 列表推导也支持多重循环，例如要把二维列表简化成一维：
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [x for row in matrix for x in row]
print(flat)
# >>> [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 如果要对二维列表中的每一个单元格取平方值，也就是多用一对中括号的事，依旧不难理解：
squared =[[x**2 for x in row] for row in matrix]
print(squared)
# >>> [[1, 4, 9], [16, 25, 36], [49, 64, 81]]

# 如果表达式里还有一层循环，那么列表推导就会变得很长，这时候必须分成多行来写才看得清楚一些
my_lists = [
    [[1, 2, 3], [4, 5, 6]]
]
flat = [x for sublist1 in my_lists
        for sublist2 in sublist1
        for x in sublist2]
# 可以看出，此时的列表推导并没有比普通的写法更加简洁，反而用循环语句看起来更清晰
flat = []
for sublist1 in my_lists:
    for sublist2 in sublist1:
        flat.extend(sublist2)

# 列表推导也支持多个 if 条件，处在同一循环级别中的多项条件，彼此间默认形成 and 表达式
# 例如要从数字列表中选出大于 4 的偶数，那么下面这两种列表推导方式是等效的
a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
b = [x for x in a if x > 4 if x % 2 == 0]
c = [x for x in a if x > 4 and x % 2 == 0]

# 每一级循环的 for 表达式后面都可以指定条件
# 例如要从原矩阵中把那些本身能为 3 所整除，且其所在行的各元素之和又大于 10 的单元格找出来
# 虽然列表推导可以实现，但是这样的代码很难懂：
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
filtered = [[x for x in row if x % 3 == 0]
            for row in matrix if sum(row) >= 10]
print(filtered)
# >>>[[6], [9]]
# 不建议便携这种包含复杂式子的列表推导，这样会使其他人很难理解这段代码
# 虽然能省下几行空间，但却会给稍后阅读代码的人带来很大障碍

"""
列表推导的缺点在于，对于输入序列中的每个值来说，可能都要创建仅含一项元素的全新列表
如果输入的数据非常多，可能会消耗大量内存，并导致程序崩溃
为解决此问题，python 提供了生成器表达式（generator expression）
它是对列表推导和生成器对一种泛化
生成器表达式在运行的时候，并不会把整个输出序列都呈现出来，而是会估值为迭代器
这个迭代器每次可以根据生成器表达式产生一项数据
"""
# 把实现列表推导所用的那种写法放在一对圆括号内，就构成了生成器表达式
matrix = [[1, 2], [3, 4, 5, 6], [7, 8, 9], [10]]
it = (len(row) for row in matrix)
print(it)
# >>> <generator object <genexpr> at 0x10e0b6660>

# 逐次调用内置的 next 函数，可使其按照生成器表达式来输出下一个值
# 可以根据自己的需要多次调用来生成新值，不用担心内存用量激增
print(next(it))
print(next(it))
# >>> 2
# >>> 4

# 使用生成器表达式还有个好处，就是可以相互组合
# 比如把一个生成器表达式所返回的迭代器用作另一个生成器表达式对输入值
roots = ((x, x**0.5) for x in it)
print(next(roots))
# >>> (3, 1.7320508075688772)

# 外围对迭代器每次前进时，都会推动内部的那个迭代器，这就产生了连锁反应
# 使得执行循环、评估条件表达式、对接输入和输出等逻辑都组合在了一起
# 比如上述的外围迭代器执行过一次后，内部的也执行了一次
# 对于内部的迭代器，现在只剩下一个值
print(next(it))
# >>> 1
# 需要注意，迭代器是有状态的，用过一轮后，就不要反复使用了
