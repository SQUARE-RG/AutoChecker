#include <stdio.h>

extern "C" char *gets(char *);

int main()
{
    char line[8] = {0};
    printf("Input a string:");
    gets(line); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-18]
    printf("The line entered was:%s\n", line);
    return 0;
}
