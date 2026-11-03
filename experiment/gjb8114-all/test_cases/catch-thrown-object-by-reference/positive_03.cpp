#include <iostream>

class Base {
public:
    virtual ~Base() = default;
    virtual int code() const { return 1; }
};

class Derived : public Base {
public:
    int code() const override { return 2; }
};

int main() {
    try {
        throw Derived();
    }
    catch (Base& e) {
        std::cout << e.code() << '\n';
    }
    return 0;
}
