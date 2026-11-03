#include <cstdarg>

static int sum_variadic(int count, ...)
{
    std::va_list args;
    va_start(args, count);
    int total = 0;
    for (int i = 0; i < count; ++i) {
        total += va_arg(args, int);
    }
    va_end(args);
    return total;
}

int main()
{
    return sum_variadic(2, 3, 4);
}
