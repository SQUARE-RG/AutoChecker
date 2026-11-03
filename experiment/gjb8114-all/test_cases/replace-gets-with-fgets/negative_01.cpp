#include <stdio.h>

extern "C" char *gets(char *s);

int main(void)
{
    char line[16] = {0};
    printf("Input a string: ");
    if (gets(line) == NULL) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-18]
    {
        printf("gets error\n");
        return -1;
    }
    printf("The line entered was: %s\n", line);
    return 0;
}
