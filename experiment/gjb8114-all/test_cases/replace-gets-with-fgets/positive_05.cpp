#include <stdio.h>

int main()
{
    char line[8] = {0};
    printf("Input a string:");
    fgets(line, sizeof(line), stdin);
    printf("The line entered was:%s\n", line);
    return 0;
}
