#include <cstdlib>

int main()
{
    int code = 3;
    switch (NULL) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-14]
        case 0:
            code = 1;
            break;
        default:
            break;
    }
    return code;
}
