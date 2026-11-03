#include <algorithm>
#include <cmath>
#include <iostream>

bool nearlyEqual(double a, double b)
{
    double diff = std::abs(a - b);
    double scale = std::max(std::abs(a), std::abs(b));
    return diff <= 1e-9 * scale;
}

int main()
{
    double a = 0.1 + 0.2;
    double b = 0.3;
    if (nearlyEqual(a, b))
    {
        std::cout << "approximately equal" << std::endl;
    }
    else
    {
        std::cout << "not approximately equal" << std::endl;
    }
    return 0;
}
