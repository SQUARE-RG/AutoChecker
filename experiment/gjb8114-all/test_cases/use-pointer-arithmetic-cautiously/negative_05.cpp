#include <iostream>

int main() {
    int values[] = {10, 20, 30, 40, 50};
    int* current = &values[4];
    --current; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-3]
    std::cout << *current << std::endl;
    return 0;
}
