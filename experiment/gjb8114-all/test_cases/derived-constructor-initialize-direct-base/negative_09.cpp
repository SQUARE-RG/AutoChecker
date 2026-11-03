#include <cstdint>

class Base {
public:
    int b;
    constexpr Base() : b(0) {}
    constexpr explicit Base(int v) : b(v) {}
};

class Derived : public Base {
public:
    int d;
    constexpr Derived() : d(1) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-5]
    {}
};

int main() {
    Derived obj;
    return obj.d;
}
