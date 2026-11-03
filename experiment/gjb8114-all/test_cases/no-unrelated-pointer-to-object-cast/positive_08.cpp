#include <iostream>

struct Base {
    int baseValue;
};

struct Derived : Base {
    int derivedValue;
};

int main() {
    Derived derived;
    Base* basePtr = static_cast<Base*>(&derived);
    (void)basePtr;
    return 0;
}
