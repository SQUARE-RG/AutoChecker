#include <iostream>

class Foo {
public:
    explicit Foo(int value) : a(value) {}
    int get() const { return a; }
private:
    int a;
};

int main() {
    Foo thef(42);
    return thef.get() == 42 ? 0 : 1;
}
