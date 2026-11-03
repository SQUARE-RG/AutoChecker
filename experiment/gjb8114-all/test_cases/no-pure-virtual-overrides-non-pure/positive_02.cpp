#include <iostream>

class Base {
public:
    virtual ~Base() = default;
    virtual void process(int value) {}
};

class Derived : public Base {
public:
    ~Derived() override = default;
    virtual void process(double value) = 0;
};

int main() {
    Base b;
    b.process(1);
    return 0;
}
