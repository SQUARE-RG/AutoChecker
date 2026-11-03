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
    constexpr Derived() : Base(1), d(2) {}
};

int main() {
    Derived obj;
    return obj.d;
}
