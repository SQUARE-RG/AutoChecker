#include <iostream>

class AbstractBase {
public:
    AbstractBase() : kind(0) {}
    virtual ~AbstractBase() = default;
    virtual void f() = 0;
protected:
    AbstractBase& operator=(AbstractBase const& rhs) {
        kind = rhs.kind;
        return *this;
    }
private:
    int kind;
};

class Derived : public AbstractBase {
public:
    Derived() : AbstractBase(), member(0) {}
    ~Derived() override = default;
    void f() override {}
private:
    int member;
};

int main() {
    Derived d;
    return 0;
}
