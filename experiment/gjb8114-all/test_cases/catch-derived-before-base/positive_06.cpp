#include <iostream>

class Parent {
public:
    Parent() = default;
    virtual ~Parent() = default;
};

class Child : public Parent {
public:
    Child() = default;
};

int main() {
    try {
        throw Child{};
    } catch (Child& c) {
        std::cout << "Caught child by non-const reference\n";
        (void)c;
    } catch (const Parent& p) {
        std::cout << "Caught parent by const reference\n";
        (void)p;
    }
    return 0;
}
