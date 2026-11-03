#include <iostream>
#include <type_traits>

int category()
{
    if constexpr (std::is_floating_point_v<int>)
    {
        return 1;
    }
    else if constexpr (std::is_integral_v<int>) return 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-2]
    else
    {
        return 3;
    }
}

int main()
{
    std::cout << category() << std::endl;
    return 0;
}
