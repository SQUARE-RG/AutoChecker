#include <cstdlib>

int main()
{
    int value = 3;
    if (/* outer comment begins here
         /* nested comment start */ value > 0) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-6]
        return EXIT_SUCCESS;
    }
    return EXIT_FAILURE;
}
