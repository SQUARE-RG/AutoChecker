#include <iostream>

bool evaluate(bool flag, bool ready, bool timeout)
{
    if (flag || ((!ready) && timeout))
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
