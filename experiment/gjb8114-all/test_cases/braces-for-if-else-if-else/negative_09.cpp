#include <iostream>

int adjusted(int n)
{
    if (int doubled = n * 2; doubled > 10) return doubled; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-2]
    return n;
}

int main()
{
    std::cout << adjusted(6) << std::endl;
    return 0;
}
