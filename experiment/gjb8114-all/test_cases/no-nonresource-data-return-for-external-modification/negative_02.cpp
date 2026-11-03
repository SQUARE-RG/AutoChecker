#include <iostream>

class B {
private:
    int value = 1;
public:
    int* get_value() { return &value; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-3]
};

int main() {
    B b;
    *b.get_value() = 42;
    return 0;
}
