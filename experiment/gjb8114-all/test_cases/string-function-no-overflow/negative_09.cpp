#include <string.h>
#include <stdio.h>

int main()
{
    char dest[2][8] = {{0}};
    strcpy(dest[0], "12345678"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-19]
    printf("%s\n", dest[0]);
    return 0;
}
