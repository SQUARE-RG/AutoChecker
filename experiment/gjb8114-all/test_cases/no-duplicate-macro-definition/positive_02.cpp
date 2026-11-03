#include <cstdio>

#if defined(USE_WIDE)
#define VALUE_TYPE long
#else
#define VALUE_TYPE int
#endif

static VALUE_TYPE accumulate(VALUE_TYPE seed)
{
    VALUE_TYPE total = seed;
    for (int i = 0; i < 3; ++i) {
        total = static_cast<VALUE_TYPE>(total + i);
    }
    return total;
}

int main(void)
{
    VALUE_TYPE v = accumulate(static_cast<VALUE_TYPE>(10));
    std::printf("%ld\n", static_cast<long>(v));
    return 0;
}
