#include <string.h>
#include <stdio.h>

int main()
{
    char dest[11] = "123456";
    char src[] = "7890";
    strcat(dest, src);
    printf("%s\n", dest);
    return 0;
}
