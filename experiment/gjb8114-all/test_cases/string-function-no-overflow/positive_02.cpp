#include <cstring>
#include <cstdio>

int main()
{
    char string2[12] = "abc";
    std::strncat(string2, "overflow", 9);
    std::printf("string2=%s\n", string2);
    return 0;
}
