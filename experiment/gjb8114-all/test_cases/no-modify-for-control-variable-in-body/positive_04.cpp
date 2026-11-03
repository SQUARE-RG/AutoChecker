#include <iostream>

int main()
{
    int values[5] = {0, 0, 0, 0, 0};
    for (int i = 0; i < 5; ++i)
    {
        values[i] = i * 2;
    }
    std::cout << values[0] << std::endl;
    return 0;
}
