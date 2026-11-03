#include <iostream>

class B {
public:
    B() : kind(0) {}
    virtual ~B() = default;
    virtual void f() = 0;
    B& operator=(B const &rhs) = delete; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-4]
private:
    int kind;
};

class D : public B {
public:
    D() : B(), member(0) {}
    ~D() override = default;
    void f() override {}
private:
    int member;
};

int main() {
    D d;
    d.f();
    return 0;
}
