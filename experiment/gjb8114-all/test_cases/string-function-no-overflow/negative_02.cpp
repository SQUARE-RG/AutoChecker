#include <cstring>
#include <cstdio>

int main()
{
    char string2[10] = "abc";
    std::strncat(string2, "overflow", 9); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-19]
    std::printf("string2=%s\n", string2);
    return 0;
}
