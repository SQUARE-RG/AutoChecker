#include <cstring>
#include <cstdio>

int main()
{
    char dst[6] = "ab";
    std::strcat(dst, "XYZ");
    std::printf("%s\n", dst);
    return 0;
}
