#include <cstdio>

int main()
{
    char buffer[16] = {0};
    do {
        std::printf("Input: ");
    } while (std::fgets(buffer, static_cast<int>(sizeof(buffer)), stdin) != nullptr);
    std::printf("last line: %s\n", buffer);
    return 0;
}
