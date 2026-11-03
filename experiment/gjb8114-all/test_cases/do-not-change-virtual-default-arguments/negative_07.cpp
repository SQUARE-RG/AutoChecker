#include <iostream>

class Base {
public:
    virtual ~Base() = default;
    virtual int compute(int a = 10, int b = 20) const {
        return a + b;
    }
};

class Derived : public Base {
public:
    int compute(int a = 30, int b = 40) const override { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-1]
        return a + b;
    }
};

int main() {
    Derived d;
    Base& b = d;
    return b.compute();
}
