#include <iostream>

class A {
private:
    int n = 1;
public:
    int& get_n() { return n; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-3]
};

int main() {
    A a;
    a.get_n() = 10;
    return 0;
}
