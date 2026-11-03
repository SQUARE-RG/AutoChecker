#include <string.h>
#include <stdio.h>

int main(void)
{
    char buffer[9] = "abc";
    strcat(buffer, "defgh");
    printf("%s\n", buffer);
    return 0;
}
