#include <iostream>

int* pick(int* external, bool useLocal) {
    int local = 42;
    return useLocal ? &local : external; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-4]
}

int main() {
    int value = 7;
    int* p = pick(&value, false);
    std::cout << *p << std::endl;
    return 0;
}
