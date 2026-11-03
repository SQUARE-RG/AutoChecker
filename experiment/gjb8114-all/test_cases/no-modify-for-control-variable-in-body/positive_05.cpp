#include <iostream>

int main()
{
    int count = 10;
    int sum = 0;
    for (int i = 0; i < 5; ++i)
    {
        --count;
        sum += i;
    }
    std::cout << count << ' ' << sum << std::endl;
    return 0;
}
