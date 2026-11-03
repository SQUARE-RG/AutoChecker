#include <stdio.h>

extern "C" char *gets(char *);

int main()
{
    char line[8] = {0};
    printf("Input a string:");
    char *result = gets(line) != nullptr ? line : nullptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-18]
    if (result != nullptr)
    {
        printf("The line entered was:%s\n", line);
    }
    return 0;
}
