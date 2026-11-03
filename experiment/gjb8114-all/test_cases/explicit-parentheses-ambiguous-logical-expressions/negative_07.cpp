#include <iostream>

bool evaluate(bool flag, bool ready, bool timeout)
{
    if (flag || !ready && timeout) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-4]
    {
        return true;
    }
    return false;
}

int main()
{
    bool flag = true;
    bool ready = false;
    bool timeout = true;
    bool result = evaluate(flag, ready, timeout);
    std::cout << result << std::endl;
    return 0;
}
