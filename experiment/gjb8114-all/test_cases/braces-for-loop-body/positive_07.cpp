#include <iostream>

int main()
{
    int total = 0;
    for (int i = 0; i < 10; ++i)
    {
        continue;
    }
    std::cout << total << '\n';
    return 0;
}
