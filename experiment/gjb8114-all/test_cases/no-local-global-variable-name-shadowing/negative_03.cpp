#include <cstdio>

int total = 0;

int main()
{
    for (int total = 0; total < 3; ++total) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-1]
    {
        std::printf("%d\n", total);
    }
    return 0;
}
