#include <cstdio>

int main()
{
    char line[16] = {0};
    if (char *p = std::fgets(line, static_cast<int>(sizeof line), stdin); p != nullptr)
    {
        std::printf("The line entered was: %s\n", line);
    }
    else
    {
        std::printf("fgets error\n");
        return 1;
    }
    return 0;
}
