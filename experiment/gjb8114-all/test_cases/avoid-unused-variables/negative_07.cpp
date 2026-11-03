#include <iostream>

int main() {
    double unused_rate = 0.75; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-2]
    std::cout << "done\n";
    return 0;
}
