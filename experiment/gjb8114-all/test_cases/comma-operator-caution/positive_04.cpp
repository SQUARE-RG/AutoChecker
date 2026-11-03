#include <iostream>

int main()
{
    int values[3];
    values[0] = 10;
    values[1] = 20;
    values[2] = 30;
    int index = 0;
    int position = index + 1;
    int value = values[position];
    std::cout << value << '\n';
    return 0;
}
