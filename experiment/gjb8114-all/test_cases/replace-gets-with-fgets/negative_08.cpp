#include <stdio.h>

extern "C" char *gets(char *);

int main(void)
{
    char line[16] = {0};
    switch (gets(line) != nullptr) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-18]
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
