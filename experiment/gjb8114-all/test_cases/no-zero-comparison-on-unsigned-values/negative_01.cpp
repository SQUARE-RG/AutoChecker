#include <cstdint>

int main()
{
    unsigned int x = 1;
    int flag = 0;
    if (x >= 0) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-4]
        flag = flag + 1;
    }
    return flag;
}
