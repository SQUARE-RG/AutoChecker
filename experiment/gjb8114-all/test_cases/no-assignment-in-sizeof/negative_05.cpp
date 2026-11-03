#include <iostream>

int main()
{
    int x = 1, y = 2, cond = 1;
    std::size_t ilen = sizeof(cond ? (x = y) : x); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-13]
    std::cout << ilen << std::endl;
    return 0;
}
