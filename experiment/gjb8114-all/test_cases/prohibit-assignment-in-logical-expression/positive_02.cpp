#include <cstdio>

int main()
{
    int limit = 0;
    int count = 0;
    limit = 4;
    while (count < limit && count >= 0)
    {
        ++count;
    }
    std::printf("%d %d\n", count, limit);
    return 0;
}
