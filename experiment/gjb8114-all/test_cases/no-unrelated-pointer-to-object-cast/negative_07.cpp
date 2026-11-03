#include <iostream>

struct Target {
    int value;
};

int main() {
    int n = 0;
    int* p = &n;
    int** pp = &p;
    Target* target = reinterpret_cast<Target*>(pp); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-1]
    (void)target;
    return 0;
}
