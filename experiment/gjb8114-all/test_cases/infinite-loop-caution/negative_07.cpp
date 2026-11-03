#include <iostream>

int main() {
    int counter = 0;
    do { ++counter; } while (1);
    // CHECK-MESSAGES: :[[@LINE-1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-1]
}
