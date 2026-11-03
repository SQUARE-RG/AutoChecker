#include <cstring>

int main()
{
    char src[] = "overflow";
    char dst[8] = {0};
    std::strcpy(dst, src); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-15]
    return 0;
}
