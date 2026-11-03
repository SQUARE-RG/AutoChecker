#include <iostream>

struct A {
    int a;
    A() : a(1) {}
};

struct B {
    int b;
    B() : b(2) {}
};

struct C : A, B {
    int c;
    C() : A(), B(), c(3) {}
};

int main() {
    try {
        throw C();
    }
    catch (C& e) {
        std::cout << e.c << '\n';
    }
    catch (A& e) {
        std::cout << e.a << '\n';
    }
    return 0;
}
