#include <string>
#include <iostream>

int main()
{
    char buffer[4] = {'a', 'b', 'c', 'd'};
    std::string text(buffer, 8); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-14]
    std::cout << text.size();
    return 0;
}
