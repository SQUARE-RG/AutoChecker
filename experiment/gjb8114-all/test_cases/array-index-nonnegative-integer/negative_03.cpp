#include <cstdlib>

int main()
{
    int data[4] = {0, 0, 0, 0};
    int offset = 1;
    data[offset - 2] = 7; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-9]
    return EXIT_SUCCESS;
}
