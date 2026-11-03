#include <string.h>
#include <stdio.h>

int main(void)
{
    char destination[16] = {0};
    strcpy(destination, "Hello world");
    printf("%s\n", destination);
    return 0;
}
