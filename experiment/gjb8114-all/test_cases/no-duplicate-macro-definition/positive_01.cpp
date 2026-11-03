#include <cstdio>

#define BLOCKDEF 1U

static unsigned int first_value(void)
{
    return BLOCKDEF;
}

#undef BLOCKDEF

#define BLOCKDEF 2U

static unsigned int second_value(void)
{
    return BLOCKDEF;
}

int main(void)
{
    std::printf("%u %u\n", first_value(), second_value());
    return 0;
}
