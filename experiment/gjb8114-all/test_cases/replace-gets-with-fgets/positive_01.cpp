#include <stdio.h>

int main(void)
{
    char line[16] = {0};
    printf("Input a string: ");
    if (fgets(line, sizeof(line), stdin) == NULL)
    {
        printf("fgets error\n");
        return -1;
    }
    printf("The line entered was: %s\n", line);
    return 0;
}
