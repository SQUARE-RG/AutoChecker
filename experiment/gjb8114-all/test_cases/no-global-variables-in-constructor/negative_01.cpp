#include <iostream>

int gVar = 10;

class Foo {
public:
    Foo();
    ~Foo();
private:
    int a;
};

Foo::Foo() {
    a = gVar; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-1]
}

Foo::~Foo() {}

int main() {
    Foo thef;
    return 0;
}
