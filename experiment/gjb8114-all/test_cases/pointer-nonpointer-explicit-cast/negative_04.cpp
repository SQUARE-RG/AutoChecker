#include <cstddef>

int main()
{
    int* ptr = nullptr;
    ptr = nullptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-5]
    return 0;
}
