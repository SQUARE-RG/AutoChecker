#include <iostream>

class Base {
public:
    virtual ~Base() = default;
    virtual int compute(int a = 1) const;
};

int Base::compute(int a) const {
    return a + 1;
}

struct Derived : Base {
    virtual int compute(int a = 1) const;
};

int Derived::compute(int a) const {
    return a + 2;
}

int main() {
    Derived d;
    Base& b = d;
    int i = b.compute();
    int j = d.compute();
    return (i + j) > 0 ? 0 : 1;
}
