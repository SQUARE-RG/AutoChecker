#include <iostream>

int main() {
    int counter = 0;
    for (;;) { ++counter; }
    // CHECK-MESSAGES: :[[@LINE-1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-1]
}
