#include <cstdio>

static int step(int v)
{
    return v + 1;
}

int main()
{
    int value = 0;
    int sum = 0;
    while ((value = step(value)) < 5 && sum < 10) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-3]
    {
        sum += value;
    }
    std::printf("%d %d\n", value, sum);
    return 0;
}
