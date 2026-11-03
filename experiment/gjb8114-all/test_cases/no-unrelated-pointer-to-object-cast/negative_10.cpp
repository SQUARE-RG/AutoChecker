#include <iostream>

class C {
public:
    int value;
};

union U {
    int i;
    float f;
};

int main() {
    C c;
    c.value = 5;
    U* u = reinterpret_cast<U*>(&c); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-1]
    (void)u;
    std::cout << c.value << std::endl;
    return 0;
}
