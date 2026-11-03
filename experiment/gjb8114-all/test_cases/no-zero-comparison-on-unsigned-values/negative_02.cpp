#include <cstdint>

int main()
{
    unsigned int y = 2;
    int flag = 0;
    int result = (y <= 0) ? 1 : 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-4]
    flag = flag + result;
    return flag;
}
