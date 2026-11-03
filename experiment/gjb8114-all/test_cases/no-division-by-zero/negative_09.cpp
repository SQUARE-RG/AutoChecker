#include <cstdint>

int main()
{
    int a = 100;
    int b = 5;
    int c = a / static_cast<int>(0u); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-12]
    return c + b;
}
