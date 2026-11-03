#include <cstring>
#include <cstdio>

int main()
{
    char dst[5] = {0};
    const char* src = "AB";
    std::strncpy(dst, src, 5);
    std::printf("%s\n", dst);
    return 0;
}
