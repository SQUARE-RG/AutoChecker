#include <iostream>

int main()
{
    int selector;
    switch (selector) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-1]
    {
        case 0:
            std::cout << "zero" << '\n';
            break;
        default:
            std::cout << "other" << '\n';
            break;
    }
    return 0;
}
