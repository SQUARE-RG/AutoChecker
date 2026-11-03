#include <string.h>
#include <stdio.h>

int main()
{
    char dest[2][9] = {{0}};
    strcpy(dest[0], "12345678");
    printf("%s\n", dest[0]);
    return 0;
}
