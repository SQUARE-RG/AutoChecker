#include <string.h>
#include <stdio.h>

int main(void)
{
    char buffer[8] = "abc";
    strcat(buffer, "defgh"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-19]
    printf("%s\n", buffer);
    return 0;
}
