#include <cmath>
#include <iostream>

int main()
{
    double a = 0.1 + 0.2;
    double b = 0.3;
    const double eps = 1e-9;
    bool equal = std::abs(a - b) <= eps;
    std::cout << equal << std::endl;
    return 0;
}
