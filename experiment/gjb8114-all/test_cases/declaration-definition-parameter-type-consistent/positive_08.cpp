#include <iostream>

int get_value(volatile int value);

int main()
{
    int x = 7;
    std::cout << get_value(x) << std::endl;
    return 0;
}

int get_value(int value)
{
    return value;
}
