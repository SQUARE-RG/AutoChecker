#include <iostream>

int adjusted(int n)
{
    if (int doubled = n * 2; doubled > 10)
    {
        return doubled;
    }
    else
    {
        return n;
    }
}

int main()
{
    std::cout << adjusted(6) << std::endl;
    return 0;
}
