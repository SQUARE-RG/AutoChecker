#include <climits>
#include <iostream>

int main()
{
    int x = 0;
    std::cin >> x;
    int result = 0;
    if (x > INT_MIN)
    {
        result = 1;
    }
    else
    {
        result = 2;
    }
    return result;
}
