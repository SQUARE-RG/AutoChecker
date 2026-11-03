#include <cstddef>

int* localArrayElement()
{
    int values[4] = {10, 20, 30, 40};
    return &values[1]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-4]
}
