#include <cstddef>

int main()
{
    int values[4] = {0, 1, 2, 3};
    values[-1] = 42; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-8]
    return 0;
}
