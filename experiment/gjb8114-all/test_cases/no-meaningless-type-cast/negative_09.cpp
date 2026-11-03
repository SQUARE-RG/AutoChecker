#include <iostream>

int main()
{
    int values[3] = {10, 20, 30};
    unsigned long index = 1;
    return values[static_cast<unsigned long>(index)]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-6]
}
