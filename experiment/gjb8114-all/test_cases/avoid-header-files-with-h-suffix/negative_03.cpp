#include <string.h> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-4]
int main()
{
    return strlen("hello") == 5 ? 0 : 1;
}
