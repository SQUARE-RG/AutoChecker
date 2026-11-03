#include <cstdlib>

int main()
{
    int flags = 0x10;
    int combined = flags | NULL; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-14]
    return combined;
}
