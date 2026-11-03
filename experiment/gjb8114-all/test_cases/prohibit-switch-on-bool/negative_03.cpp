#include <iostream>

bool isEnabled() { return true; }

int main()
{
    int result = 0;
    switch (isEnabled()) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-4]
        case 1:
            result = 10;
            break;
        case 0:
            result = 20;
            break;
    }
    return result;
}
