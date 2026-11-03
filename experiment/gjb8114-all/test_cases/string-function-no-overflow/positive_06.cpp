#include <cstring>

int main()
{
    char dest[7] = "Hi";
    const char* src = "abc";
    std::strncat(dest, src, 5);
    return 0;
}
