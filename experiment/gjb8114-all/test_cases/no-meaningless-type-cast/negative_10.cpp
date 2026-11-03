#include <iostream>

int main()
{
    int selector = 2;
    switch ((int)selector) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-6]
        case 1:
            return 1;
        case 2:
            return 0;
        default:
            return -1;
    }
}
