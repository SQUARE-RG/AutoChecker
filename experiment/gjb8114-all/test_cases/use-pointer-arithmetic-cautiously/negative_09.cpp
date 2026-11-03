#include <iostream>

static void print_value(const int* value) {
    std::cout << *value << '\n';
}

int main() {
    int arr[3] = {10, 20, 30};
    int* p = arr;
    print_value(p + 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-3]
    return 0;
}
