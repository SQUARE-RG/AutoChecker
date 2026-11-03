#include <iostream>

enum Direction { north, south, east, west };

int travel(int north_value)
{
    return north_value + static_cast<int>(north);
}

int main()
{
    std::cout << travel(1) << '\n';
    return 0;
}
