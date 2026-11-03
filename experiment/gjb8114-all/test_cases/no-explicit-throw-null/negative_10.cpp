#include <iostream>
using namespace std;

int main(void)
{
    int count = 0;
    do
    {
        ++count;
        if (count == 2)
        {
            throw NULL; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-5]
        }
    } while (count < 3);
    return 0;
}
