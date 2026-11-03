#include <cstring>
#include <cstdio>

int main()
{
    char string1[12] = {0};
    std::strncpy(string1, "Hello world", 11);
    std::printf("string1=%s\n", string1);
    return 0;
}
