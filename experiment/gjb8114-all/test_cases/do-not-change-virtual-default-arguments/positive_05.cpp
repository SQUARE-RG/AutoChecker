#include <iostream>

class Base {
public:
    virtual ~Base() = default;
    virtual int mix(int a, int b, int c = 7) const;
};

int Base::mix(int a, int b, int c) const {
    return a + b + c;
}

class Derived : public Base {
public:
    int mix(int a, int b, int c = 7) const override;
};

int Derived::mix(int a, int b, int c) const {
    return a - b - c;
}

int main() {
    Base base;
    Derived derived;
    int x = base.mix(3, 4);
    int y = derived.mix(5, 2);
    int z = derived.mix(1, 2, 3);
    std::cout << x + y + z << '\n';
    return 0;
}
