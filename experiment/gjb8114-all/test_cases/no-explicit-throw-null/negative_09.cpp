#include <iostream>
using namespace std;

int main(void)
{
    for (int i = 0; i < 3; ++i)
    {
        if (i == 1)
        {
            throw NULL; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-5]
        }
    }
    return 0;
}
