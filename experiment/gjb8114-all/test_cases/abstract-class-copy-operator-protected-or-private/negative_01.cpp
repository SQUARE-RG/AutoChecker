#include <iostream>

class AbstractBase {
public:
    AbstractBase();
    virtual ~AbstractBase();
    virtual void f() = 0;
    AbstractBase& operator=(AbstractBase const& rhs); // CHECK-MESSAGES: :[[@LINE]]:5: warning: abstract class copy assignment operator must be protected or private [ucassaat-r-2-1-4]
private:
    int kind;
};

AbstractBase::AbstractBase() : kind(0) {}
AbstractBase::~AbstractBase() {}
AbstractBase& AbstractBase::operator=(AbstractBase const& rhs) {
    kind = rhs.kind;
    return *this;
}

class Derived : public AbstractBase {
public:
    Derived() : AbstractBase(), member(0) {}
    ~Derived() override {}
    void f() override {}
private:
    int member;
};

int main() {
    Derived d;
    return 0;
}
