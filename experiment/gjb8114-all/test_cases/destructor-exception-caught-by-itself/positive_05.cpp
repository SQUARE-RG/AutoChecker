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
        throw "destructor failure";
    } catch (const char* reason) {
        std::cout << reason << std::endl;
    }
}

int main() {
    Foo f;
    return 0;
}
