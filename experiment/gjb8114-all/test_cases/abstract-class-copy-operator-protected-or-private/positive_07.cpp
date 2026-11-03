#include <iostream>

class B {
public:
    B() : kind(0) {}
    virtual ~B() = default;
    virtual void f() = 0;
protected:
    auto operator=(B const &rhs) -> B&;
private:
    int kind;
};

auto B::operator=(B const &rhs) -> B& {
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
    D d;
    d.f();
    return 0;
}
