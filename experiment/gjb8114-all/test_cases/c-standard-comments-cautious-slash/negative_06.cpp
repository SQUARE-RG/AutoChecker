#include <iostream>

#define SQUARE(x) ((x) * (x)) // simple macro
// CHECK-MESSAGES: :[[@LINE-1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-2-3]

int main() {
    std::cout << SQUARE(3) << '\n';
    return 0;
}
