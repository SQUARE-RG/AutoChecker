from abc import ABC, abstractmethod

class Animal(ABC):  # 抽象基类
    def __init__(self, name, age):
        self.name = name
        self.age = age

    @abstractmethod
    def make_sound(self):  # 这是一个抽象方法，子类必须实现
        pass

    # 在抽象类中定义 __str__ 的默认实现
    def __str__(self):
        return f"Animal: name={self.name}, age={self.age}"

class Dog(Animal):
    def __init__(self, name, age, breed):
        super().__init__(name, age)
        self.breed = breed

    def make_sound(self):  # 实现抽象方法
        return "Woof!"

    # 子类Dog重写了 __str__ 方法，提供更具体的信息
    def __str__(self):
        return f"Dog: name={self.name}, age={self.age}, breed={self.breed}"

class Cat(Animal):
    def __init__(self, name, age):
        super().__init__(name, age)

    def make_sound(self):  # 实现抽象方法
        return "Meow!"

    # 子类Cat没有重写 __str__，将使用抽象类中的默认实现

# 测试
dog = Dog("Buddy", 5, "Golden Retriever")
cat = Cat("Whiskers", 3)

print(dog)  # 输出: Dog: name=Buddy, age=5, breed=Golden Retriever
print(cat)  # 输出: Animal: name=Whiskers, age=3 (使用了抽象类的默认__str__)