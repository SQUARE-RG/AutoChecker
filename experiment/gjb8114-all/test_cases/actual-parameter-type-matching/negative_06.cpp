#include <cstdio>

int readSampleCount()
{
    return 3;
}

unsigned int scale(unsigned int factor)
{
    return factor * 2U;
}

int main()
{
    unsigned int scaled = scale(readSampleCount());  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-2]
    printf("%u\n", scaled);
    return 0;
}
