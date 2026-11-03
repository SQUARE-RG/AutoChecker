#include <iostream>

struct Multiplier
{
    int multiply(int lhs, int rhs) const
    {
        return lhs * rhs;
    }
};

int main()
{
    Multiplier multiplier;
    int result = multiplier.multiply(2, 3.5); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-2]
    std::cout << result << std::endl;
    return 0;
}
