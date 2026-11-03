#include <cstring>

int main()
{
    char src[4] = {'a', 'b', 'c', '\0'};
    char dest[8] = {0};
    std::strncpy(dest, src, sizeof(src));
    return 0;
}
