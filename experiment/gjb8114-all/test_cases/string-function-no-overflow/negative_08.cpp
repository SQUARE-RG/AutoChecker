#include <cstring>
#include <cstdio>

int main()
{
    char dst[4] = {0};
    const char* src = "AB";
    std::strncpy(dst, src, 5); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-19]
    std::printf("%s\n", dst);
    return 0;
}
