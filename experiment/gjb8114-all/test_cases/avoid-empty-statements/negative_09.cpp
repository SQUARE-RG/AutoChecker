#include <iostream>

int main() {
    int value = 0;
    if (value > 0)
        std::cout << "positive\n";
    else
        ; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-1]
    return 0;
}
