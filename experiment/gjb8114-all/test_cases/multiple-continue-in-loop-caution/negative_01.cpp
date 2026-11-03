#include <iostream>

int main() {
    int arr[] = {1, -2, 0, 3};
    int sum = 0;
    for (int x : arr) { if (x < 0) continue; if (x == 0) continue; sum += x; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-3]
    std::cout << sum << '\n';
    return 0;
}
