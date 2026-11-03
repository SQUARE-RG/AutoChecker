#include <cstdio>

int total = 0;

int main()
{
    for (int i = 0; i < 3; ++i)
    {
        total += i;
    }
    std::printf("%d\n", total);
    return 0;
}
