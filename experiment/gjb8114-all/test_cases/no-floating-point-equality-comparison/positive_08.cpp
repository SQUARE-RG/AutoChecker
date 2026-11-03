#include <cmath>
#include <iostream>

int main()
{
    double a = 1.0;
    double b = 1.0000001;
    const double eps = 1e-6;
    if (!(std::abs(a - b) < eps))
    {
        std::cout << "not approximately equal" << std::endl;
    }
    else
    {
        std::cout << "approximately equal" << std::endl;
    }
    return 0;
}
