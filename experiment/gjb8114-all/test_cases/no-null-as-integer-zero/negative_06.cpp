#include <cstddef>

int main()
{
    int values[4] = {1, 2, 3, 4};
    values[NULL] = 9; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-14]
    return values[0];
}
