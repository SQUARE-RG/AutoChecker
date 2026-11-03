#include <cstdio>

int main()
{
    char line[16] = {0};
    int count = 0;
    while (count < 3 && std::fgets(line, static_cast<int>(sizeof line), stdin) != nullptr)
    {
        std::printf("The line entered was: %s\n", line);
        ++count;
    }
    return 0;
}
