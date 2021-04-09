def f(x):
    return x ** 2
print(f(2))
def decorator(func):
    def vrapper(x):
        return func(x) + 10
    return vrapper
@decorator
def f(x):
    return x ** 2
print(f(2))
@decorator
def j(x):
    return 2*x
print(j(1))
