#include <iostream>

int main()
{
    int arr[10] = {0};
    int x;
    std::cin >> x;
    int idx = (x * 3 + 7) / 2;
    arr[idx] = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-8]
    return 0;
}
