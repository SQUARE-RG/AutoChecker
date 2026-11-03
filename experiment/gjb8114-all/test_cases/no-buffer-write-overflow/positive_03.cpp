#include <cstring>

int main()
{
    int src[4] = {1, 2, 3, 4};
    int dst[2] = {0, 0};
    std::memmove(dst, src, sizeof(dst));
    return 0;
}
