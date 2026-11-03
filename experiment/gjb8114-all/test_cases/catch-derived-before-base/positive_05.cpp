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
    } catch (Derived* d) {
        std::cout << "Caught derived pointer\n";
        delete d;
    } catch (Base* b) {
        std::cout << "Caught base pointer\n";
        delete b;
    }
    return 0;
}
