#include <iostream>

class A {
public:
    int ma = 0;
};

int main() {
    A const a1;
    A* a2 = const_cast<A*>(&a1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-2]
    (void)a2;
    return 0;
}
