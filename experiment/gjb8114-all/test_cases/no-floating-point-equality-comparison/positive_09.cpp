#include <cmath>

bool nearly_equal(double a, double b, double eps)
{
    return std::fabs(a - b) < eps;
}

int main()
{
    double x = 1.0;
    double y = 1.0000001;
    if (nearly_equal(x, y, 1e-6)) {
        return 1;
    }
    return 0;
}
