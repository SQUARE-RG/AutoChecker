#include <cstring>

int main()
{
    char src[4] = {'a', 'b', 'c', 'd'};
    char dest[8] = {0};
    std::strncpy(dest, src, sizeof(dest)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-14]
    return 0;
}
