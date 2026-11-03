#include <string>

class Base {
public:
    virtual ~Base() = default;
    virtual std::string describe(std::string prefix = std::string("base")) const {
        return prefix;
    }
};

class Derived : public Base {
public:
    std::string describe(std::string prefix = std::string("derived")) const override; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-1]
};

std::string Derived::describe(std::string prefix) const {
    return prefix;
}

int main() {
    Derived d;
    std::string result = d.describe();
    (void)result;
    return 0;
}
