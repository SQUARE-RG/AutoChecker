#include <cstring>
#include <iostream>

int main()
{
    char buf[8];
    std::strncpy(buf, "hello", sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\0';
    std::cout << buf << '\n';
    return 0;
}
