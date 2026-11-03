#include <cstdio>

int main(void)
{
    char s[16];
    const char* src = "world";
    for (int i = 0; i < 5; ++i)
        s[i] = src[i]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-16]
    std::printf("%s\n", s);
    return 0;
}
