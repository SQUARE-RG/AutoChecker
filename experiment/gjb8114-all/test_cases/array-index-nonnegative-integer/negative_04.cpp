#include <cstdlib>

enum Index : int { kNegative = -1 };

int main()
{
    int data[3] = {0, 0, 0};
    data[kNegative] = 9; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-9]
    return EXIT_SUCCESS;
}
