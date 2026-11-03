#include <iostream>

class Base {
public:
    virtual ~Base() = default;
    virtual int combine(int a = 4, int b = 9);
};

int Base::combine(int a, int b) {
    return a + b;
}

class Derived : public Base {
public:
    int combine(int a = 5, int b = 9) override; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-1]
};

int Derived::combine(int a, int b) {
    return a - b;
}

int main() {
    Base base;
    Derived derived;
    Base &ref = derived;
    int x = base.combine();
    int y = ref.combine();
    int z = derived.combine();
    std::cout << x + y + z << '\n';
    return 0;
}
