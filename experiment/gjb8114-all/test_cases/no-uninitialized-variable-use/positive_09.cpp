#include <iostream>

int main()
{
    int selector = 1;
    switch (selector)
    {
        case 0:
            std::cout << "zero" << '\n';
            break;
        default:
            std::cout << "other" << '\n';
            break;
    }
    return 0;
}
