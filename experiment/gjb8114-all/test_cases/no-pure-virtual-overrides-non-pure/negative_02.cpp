#include <iostream>

class Base {
public:
    virtual ~Base() = default;
    virtual void bar() {}
};

class Derived : public Base {
public:
    ~Derived() override = default;
    virtual void bar() override = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-3]
};

int main() {
    Base b;
    b.bar();
    return 0;
}
