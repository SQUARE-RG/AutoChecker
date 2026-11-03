#include <iostream>

class Foo {
public:
    int a;
    Foo();
    ~Foo();
};

Foo::Foo() : a(1) {}

Foo::~Foo() {
    if (a == 1) {
        throw 0; // CHECK-MESSAGES: :[[@LINE]]:9: warning: {{.*}} [ucassaat-r-2-3-2]
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
