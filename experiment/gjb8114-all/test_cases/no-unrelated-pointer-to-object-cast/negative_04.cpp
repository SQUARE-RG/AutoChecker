#include <iostream>
using namespace std;

class A {
public:
    A() : a(0) {}
    int a;
};

class B {
public:
    B() : b(0) {}
    int b;
};

int main() {
    A* pa = new A();
    pa->a = 1;
    B* pb = reinterpret_cast<B*>(pa); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-1]
    pb->b = 2;
    delete pa;
    return 0;
}
