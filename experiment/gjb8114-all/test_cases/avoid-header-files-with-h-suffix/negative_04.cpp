#include <math.h> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-4]
int main()
{
    return sqrt(16.0) == 4.0 ? 0 : 1;
}
