#include <cstddef>

int main()
{
    short sVar = 10;
    long lVar = 100000L;
    sVar += lVar; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-2]
    return static_cast<int>(sVar);
}
