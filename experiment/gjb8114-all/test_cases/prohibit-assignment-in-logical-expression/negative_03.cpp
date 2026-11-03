#include <iostream>

int compute()
{
    return 1;
}

bool check(bool ready, int& value)
{
    return ready || (value = compute()); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-3]
}

int main()
{
    int value = 0;
    bool result = check(false, value);
    std::cout << result << value << std::endl;
    return 0;
}
