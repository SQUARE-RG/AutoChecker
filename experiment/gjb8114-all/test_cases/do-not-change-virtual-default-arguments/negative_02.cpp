#include <iostream>
#include <string>

class Base {
public:
    virtual ~Base() = default;
    virtual std::string describe(const std::string& prefix = "base") const {
        return prefix + ":base";
    }
};

class Derived : public Base {
public:
    std::string describe(const std::string& prefix = "derived") const override; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-1]
};

std::string Derived::describe(const std::string& prefix) const {
    return prefix + ":derived";
}

int main() {
    Derived d;
    Base& b = d;
    std::cout << b.describe() << std::endl;
    std::cout << d.describe() << std::endl;
    return 0;
}
