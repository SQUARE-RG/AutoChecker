#include <iostream>

class Base {
public:
    virtual ~Base() = default;
    virtual void action() {}
};

class Derived : public Base {
public:
    ~Derived() override = default;
    void action() override {}
};

int main() {
    Derived d;
    d.action();
    return 0;
}
