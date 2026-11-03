#include <cstring>
#include <cstdio>

int main()
{
    char string1[10] = {0};
    std::strncpy(string1, "Hello world", 11); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-19]
    std::printf("string1=%s\n", string1);
    return 0;
}
