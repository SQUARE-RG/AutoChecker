#include <cstdio>

int main(void)
{
    int i = 0;
    int j = 0;
    if (i = 1) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-3]
    {
        j = j + 1;
    }
    std::printf("%d %d\n", i, j);
    return 0;
}
