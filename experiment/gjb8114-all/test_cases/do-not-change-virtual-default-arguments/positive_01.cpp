#include <iostream>

class Base {
public:
    virtual ~Base() = default;
    virtual int g(int a = 0);
};

int Base::g(int a) {
    return a + 1;
}

class Derived : public Base {
public:
    int g(int a = 0) override;
};

int Derived::g(int a) {
    return a + 11;
}

int main() {
    Derived d;
    Base& b = d;
    int i = b.g();
    int j = d.g();
    std::cout << i << " " << j << std::endl;
    return 0;
}
