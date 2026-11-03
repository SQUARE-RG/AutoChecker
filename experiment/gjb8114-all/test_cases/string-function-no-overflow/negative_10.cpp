#include <string.h>
#include <stdio.h>

int main()
{
    char dest[10] = "123456";
    char src[] = "7890";
    strcat(dest, src); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-19]
    printf("%s\n", dest);
    return 0;
}
