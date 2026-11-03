#include <stdio.h>
#include <string.h>

extern "C" char *gets(char *s);

int main(void)
{
    char line[32] = {0};
    printf("Enter lines, 'quit' to exit:\n");
    while (gets(line) != NULL) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-18]
    {
        if (strcmp(line, "quit") == 0)
        {
            break;
        }
        printf("Read: %s\n", line);
    }
    return 0;
}
