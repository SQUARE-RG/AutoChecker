#include <iostream>

class B {
public:
    B() : kind(0) {}
    virtual ~B() = default;
    virtual void f() = 0;
private:
    B& operator=(B const &rhs);
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
