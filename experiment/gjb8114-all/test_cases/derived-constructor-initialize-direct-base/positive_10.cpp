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
    Derived(int v) : Base(v), d(v) {}
};

int main() {
    Derived a;
    Derived b(3);
    return a.d + b.d;
}
