#include <iostream>

class Foo {
public:
    int a;
    Foo();
    ~Foo();
};

Foo::Foo() : a(1) {}

Foo::~Foo() {
    try {
        if (a == 1) {
            throw 0;
        }
    } catch (int e) {
        (void)e;
    }
}

int main() {
    try {
        Foo f;
    } catch (int e) {
        (void)e;
    }
    return 0;
}
