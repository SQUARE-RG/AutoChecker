#include <utility>

int value = 1;

int main()
{
    std::pair<int, int> p{2, 3};
    auto [first, second] = p;
    return value + first + second;
}
