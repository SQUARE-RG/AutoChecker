#include <string.h>
#include <stdio.h>

int main(void)
{
    char destination[10] = {0};
    strcpy(destination, "Hello world"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-19]
    printf("%s\n", destination);
    return 0;
}
