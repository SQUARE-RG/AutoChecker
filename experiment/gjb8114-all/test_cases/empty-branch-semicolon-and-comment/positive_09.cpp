#include <iostream>
#include <type_traits>

int main()
{
    int result = 0;
    if constexpr (std::is_integral_v<int>)
    {
        result = 11;
    }
    else
    {
        ;/* no deal with */
    }
    std::cout << result << std::endl;
    return 0;
}
