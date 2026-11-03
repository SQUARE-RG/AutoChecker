#include <iostream>

int main() {
    unsigned int u = 1;
    int count = 0;
    do {
        ++count;
        u = 0;
    } while (u >= 0 && count < 2); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-4]
    std::cout << count << '\n';
    return 0;
}
