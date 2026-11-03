#include <cstdio>

int main(void)
{
    char buf[16];
    std::snprintf(buf, sizeof(buf), "%s", "world");
    std::printf("%s\n", buf);
    return 0;
}
