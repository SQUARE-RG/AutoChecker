#include <iostream>

int main()
{
    auto is_negative = [](unsigned int value) { return value < 0; }; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-4]
    unsigned int number = 0u;
    bool result = is_negative(number);
    return result ? 0 : 1;
}
