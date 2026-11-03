#include <algorithm>
#include <iostream>
#include <string>

int main()
{
    std::string text = "yes";
    char buf[8];
    std::copy(text.begin(), text.end(), buf); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-16]
    std::cout << buf << '\n';
    return 0;
}
