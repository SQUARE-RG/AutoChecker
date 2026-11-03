#include <iostream>

class Base {
public:
    virtual ~Base() = default;
    virtual bool isEnabled(bool state = true) const {
        return state;
    }
};

class Derived : public Base {
public:
    bool isEnabled(bool state = true) const override {
        return state;
    }
};

int main() {
    Derived d;
    Base& b = d;
    bool a = b.isEnabled();
    bool c = d.isEnabled(false);
    return (a && !c) ? 0 : 1;
}
