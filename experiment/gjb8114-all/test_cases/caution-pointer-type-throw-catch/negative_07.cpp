#include <iostream>

int main()
{
    int arr[3] = {1, 2, 3};
    try
    {
        throw arr;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-2]
    }
    catch (int *p)
    {
        std::cout << p[0] << std::endl;
    }
    return 0;
}
