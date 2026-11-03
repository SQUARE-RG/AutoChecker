#include <iostream>

int compute()
{
    return 1;
}

bool check(bool ready, int value)
{
    return ready || (compute() > value);
}

int main()
{
    int value = 0;
    bool result = check(false, value);
    std::cout << result << std::endl;
    return 0;
}
