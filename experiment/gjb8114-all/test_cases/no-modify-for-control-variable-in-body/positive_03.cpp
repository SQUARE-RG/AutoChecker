#include <iostream>

int main()
{
    int total = 0;
    for (int i = 0; i < 5; ++i)
    {
        {
            int i = 10;
            i += 2;
            total += i;
        }
    }
    std::cout << total << std::endl;
    return 0;
}
