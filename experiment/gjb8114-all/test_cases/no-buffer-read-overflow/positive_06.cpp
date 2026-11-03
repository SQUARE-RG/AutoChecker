#include <cstring>

int main()
{
    char small[2] = {'A', 'B'};
    char large[4] = {'A', 'B', 'C', 'D'};
    int result = std::memcmp(small, large, sizeof(small));
    (void)result;
    return 0;
}
