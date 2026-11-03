#include <cstdint>

class Base {
public:
    int b;
    Base() : b(0) {}
    explicit Base(int v) : b(v) {}
};

class Derived : public Base {
public:
    int d;
    Derived() : Base(0), d(0) {}
    Derived(int v) : d(v) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-5]
    {}
};

int main() {
    Derived a;
    Derived b(3);
    return a.d + b.d;
}
