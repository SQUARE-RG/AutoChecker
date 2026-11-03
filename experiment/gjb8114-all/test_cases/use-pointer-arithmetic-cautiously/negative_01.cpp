#include <iostream>

int main() {
    int values[4] = {2, 4, 6, 8};
    int* ptr = values;
    int third = *(ptr + 2); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-3]
    std::cout << third << '\n';
    return 0;
}
