print("running package crudclient from __main__.py")


class DualUseMethod:
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls=None):
        if obj is None:
            # Called on the class, behave like a class method
            return lambda *args, **kwargs: self.func(cls, *args, **kwargs)
        else:
            # Called on an instance, behave like an instance method
            return lambda *args, **kwargs: self.func(obj, *args, **kwargs)


class MyClass:
    @DualUseMethod
    def my_method(self, *args):
        # You can define your function logic here
        # self will be either the class or the instance, depending on the call
        if isinstance(self, type):
            return f"Called from class, args: {args}"
        else:
            return f"Called from instance, args: {args}"


# Usage examples
print(MyClass.my_method())  # As a class method
obj = MyClass()
print(obj.my_method(1, 2, 3))  # As an instance method
