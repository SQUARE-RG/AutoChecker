#include <cstddef>

class Base {
public:
    virtual Base* instance() { return this; }
    virtual ~Base() = default;
};

class Derived : public Base {
public:
    virtual Derived* instance() = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-3]
};

int main() {
    return 0;
}
