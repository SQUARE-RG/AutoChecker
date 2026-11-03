#include <cstring>

int main()
{
    char dest[7] = {0};
    const char* src = "Hello";
    std::strncpy(dest, src, 7);
    return 0;
}
