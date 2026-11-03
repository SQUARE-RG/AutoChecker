#include <stdio.h>

int main()
{
    char line[8] = {0};
    printf("Input a string:");
    for (char *p = fgets(line, sizeof(line), stdin); p != nullptr; p = nullptr)
    {
        printf("The line entered was:%s\n", line);
    }
    return 0;
}
