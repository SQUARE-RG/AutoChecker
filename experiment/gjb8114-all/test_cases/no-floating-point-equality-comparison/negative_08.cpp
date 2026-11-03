#include <iostream>

int main()
{
    float x = 0.5f;
    float y = 1.0f / 3.0f;
    bool flag = true;
    if ((x != y) || flag) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-3]
    {
        std::cout << "different or flag" << std::endl;
    }
    else
    {
        std::cout << "same and no flag" << std::endl;
    }
    return 0;
}
