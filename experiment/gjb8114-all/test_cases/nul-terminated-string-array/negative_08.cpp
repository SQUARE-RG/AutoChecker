#include <algorithm>
#include <iostream>

int main()
{
    char buf[8];
    std::fill(buf, buf + 8, 'a'); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-16]
    std::cout << buf << '\n';
    return 0;
}
