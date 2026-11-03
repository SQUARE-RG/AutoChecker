#include <cstring>
#include <cstdio>

int main()
{
    char dst[5] = "ab";
    std::strcat(dst, "XYZ"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-19]
    std::printf("%s\n", dst);
    return 0;
}
