#include <iostream>

class Foo {
public:
    Foo();
    ~Foo();
    void SetVar(int);
private:
    int a;
};

Foo::Foo() : a(0) {}
Foo::~Foo() {}

void Foo::SetVar(int var) {
    a = var;
}

int main() {
    Foo thef;
    thef.SetVar(2);
    return 0;
}
