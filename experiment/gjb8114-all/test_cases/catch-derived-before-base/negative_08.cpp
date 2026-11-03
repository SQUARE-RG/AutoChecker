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
    catch (A& e) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-1]
        std::cout << e.a << '\n';
    }
    catch (C& e) {
        std::cout << e.c << '\n';
    }
    return 0;
}
