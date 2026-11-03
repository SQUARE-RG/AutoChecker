#include <iostream>

int main() {
    int values[] = {1, 2, 3, 4, 5};
    int* end = &values[4];
    int* middle = end - 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-3]
    std::cout << *middle << std::endl;
    return 0;
}
