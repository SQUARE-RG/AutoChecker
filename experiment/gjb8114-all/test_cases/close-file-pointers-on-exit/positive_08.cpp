#include <cstdio>

int count_lines()
{
    std::FILE* fp = std::fopen("data.txt", "r");
    if (fp == nullptr) {
        return -1;
    }

    char line[128];
    int count = 0;
    while (std::fgets(line, sizeof(line), fp) != nullptr) {
        ++count;
    }

    std::fclose(fp);
    return count;
}

int main()
{
    return count_lines();
}
