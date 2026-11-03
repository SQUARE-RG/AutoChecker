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
    int compute(int a = 1) const; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-2]
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
