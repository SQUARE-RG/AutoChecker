#include <iostream>

int main()
{
    int sum = 0;
    for (unsigned int i = 0; i >= 0; i += 5) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-4]
    {
        sum += static_cast<int>(i);
        if (i > 10)
        {
            break;
        }
    }
    return sum;
}
