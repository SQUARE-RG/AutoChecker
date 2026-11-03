#include <cstring>

int main()
{
    char src[] = "overflow";
    char dst[16] = {0};
    std::strcpy(dst, src);
    return 0;
}
