#include <cstdio>

int main()
{
    char line[16] = {0};
    std::printf("Input a string:");
    char *result = std::fgets(line, static_cast<int>(sizeof(line)), stdin);
    if (result == nullptr) {
        std::printf("fgets error\n");
        return 1;
    }
    std::printf("The line entered was:%s\n", line);
    return 0;
}
