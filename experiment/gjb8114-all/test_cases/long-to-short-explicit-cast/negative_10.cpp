#include <cstddef>

short narrow(long lVar)
{
    return lVar; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-2]
}

int main()
{
    long lVar = 100000L;
    short sVar = narrow(lVar);
    return static_cast<int>(sVar);
}
