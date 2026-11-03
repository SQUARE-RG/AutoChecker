#include <iostream>

int main()
{
    int values[5] = {1, 2, 3, 4, 5};
    int sum = 0;
    int i = 0;

    while (i < 5)
    {
        sum += values[i];
        ++i;
    }

    std::cout << sum << '\n';
    return 0;
}
