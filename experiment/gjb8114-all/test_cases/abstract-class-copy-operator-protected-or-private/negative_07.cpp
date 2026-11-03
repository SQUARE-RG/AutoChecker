#include <iostream>

class B {
public:
    B() : kind(0) {}
    virtual ~B() = default;
    virtual void f() = 0;
    virtual B& operator=(B const &rhs); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-4]
private:
    int kind;
};

B& B::operator=(B const &rhs) {
    kind = rhs.kind;
    return *this;
}

class D : public B {
public:
    D() : B(), member(0) {}
    ~D() override = default;
    void f() override {}
private:
    int member;
};

int main() {
    D d1;
    D d2;
    B &b1 = d1;
    B &b2 = d2;
    b1 = b2;
    return 0;
}
