#include <iostream>

int main() {
    int* value = new int(10);
    std::cout << *value;
    value = new int(20);  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-3]
    std::cout << *value;
    delete value;
    return 0;
}
