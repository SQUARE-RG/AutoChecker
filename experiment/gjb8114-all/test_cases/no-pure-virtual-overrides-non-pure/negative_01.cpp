#include <iostream>

class A {
public:
    virtual ~A() = default;
    virtual void foo() = 0;
};

class B : public A {
public:
    ~B() override = default;
    void foo() override {}
};

class C : public B {
public:
    ~C() override = default;
    void foo() override = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-3]
};

int main() {
    B b;
    b.foo();
    return 0;
}
