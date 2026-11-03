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
    unsigned int count = static_cast<unsigned int>(readSampleCount());
    unsigned int scaled = scale(count);
    printf("%u\n", scaled);
    return 0;
}
