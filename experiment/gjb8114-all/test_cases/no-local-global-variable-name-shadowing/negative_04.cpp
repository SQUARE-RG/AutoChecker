#include <cstdio>

int count = 0;

int main()
{
    if (int count = 5; count > 0) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-1]
    {
        std::printf("%d\n", count);
    }
    return 0;
}
