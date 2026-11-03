#include <iostream>

class Base {
public:
    Base() = default;
    virtual ~Base() = default;
};

class Derived : public Base {
public:
    Derived() = default;
};

int main() {
    try {
        throw new Derived();
    } catch (Base* b) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-1]
        std::cout << "Caught base pointer\n";
        delete b;
    } catch (Derived* d) {
        std::cout << "Caught derived pointer\n";
        delete d;
    }
    return 0;
}
