#include <iostream>

class Foo {
public:
    int a;
    Foo();
    ~Foo() noexcept(false);
};

Foo::Foo() : a(1) {}

Foo::~Foo() noexcept(false) {
    throw "destructor failure"; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-3-2]
}

int main() {
    try {
        Foo f;
    } catch (...) {
    }
    return 0;
}
