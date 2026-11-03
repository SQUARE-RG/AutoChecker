#include <stdio.h>

int main(void)
{
    char line[16] = {0};
    switch (fgets(line, sizeof line, stdin) != nullptr)
    {
    case 1:
        printf("Read: %s\n", line);
        break;
    default:
        printf("Read failed\n");
        break;
    }
    return 0;
}
