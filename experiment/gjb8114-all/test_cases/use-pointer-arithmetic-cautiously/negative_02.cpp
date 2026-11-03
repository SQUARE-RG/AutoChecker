#include <iostream>

int main() {
    int values[3] = {1, 3, 5};
    int* ptr = values;
    ++ptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-3]
    std::cout << *ptr << '\n';
    return 0;
}
