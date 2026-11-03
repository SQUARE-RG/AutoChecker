#include <cstdio>

int main(void)
{
    int x = 2;
    int z = 0;
    switch (x)
    {
        case 1:
            if (x > 0)
            {
                case 2: // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-8]
                    z = 1;
                    break;
            }
            break;
        default:
            z = 3;
            break;
    }
    return z;
}
