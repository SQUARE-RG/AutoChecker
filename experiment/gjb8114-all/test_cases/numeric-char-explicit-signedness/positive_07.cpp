#include <vector>

int main()
{
    std::vector<signed char> values = {10, 20, 30};
    int sum = static_cast<int>(values[0]) + static_cast<int>(values[1]);
    return sum;
}
