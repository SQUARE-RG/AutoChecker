#include <iostream>

enum Weekday { monday, tuesday, wednesday };

int main()
{
    int values[] = { 1, 2, 3 };
    for (int day : values)
    {
        std::cout << day << ' ' << static_cast<int>(monday) << '\n';
    }
    return 0;
}
