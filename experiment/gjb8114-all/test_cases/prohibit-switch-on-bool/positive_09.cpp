#include <iostream>

int get_mode()
{
    return 2;
}

int main()
{
    int result = 0;
    switch (get_mode())
    {
        case 1:
            result = 10;
            break;
        case 2:
            result = 20;
            break;
        default:
            result = 0;
            break;
    }
    std::cout << result << '\n';
    return 0;
}
