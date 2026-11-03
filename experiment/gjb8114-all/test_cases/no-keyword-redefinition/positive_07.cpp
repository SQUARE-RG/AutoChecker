#include <utility>

int main()
{
    auto [left, right] = std::make_pair(1, 2);
    return left + right;
}
