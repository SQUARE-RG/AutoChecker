#include <iostream>

int main() {
    int arr[4] = {10, 20, 30, 40};
    int* last = &arr[3];
    for (int i = 0; i < 4; ++i) {
        if (arr + i <= last) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-3]
            std::cout << arr[i] << '\n';
        }
    }
    return 0;
}
