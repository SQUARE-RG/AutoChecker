#include <cstdio>

int main(void)
{
    char buf[8];
    buf[0] = 'y';
    buf[1] = 'e';
    buf[2] = 's'; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-16]
    std::printf("%s\n", buf);
    return 0;
}
