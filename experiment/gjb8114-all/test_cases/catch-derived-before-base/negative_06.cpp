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
    } catch (const Parent& p) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-1]
        std::cout << "Caught parent by const reference\n";
        (void)p;
    } catch (Child& c) {
        std::cout << "Caught child by non-const reference\n";
        (void)c;
    }
    return 0;
}
