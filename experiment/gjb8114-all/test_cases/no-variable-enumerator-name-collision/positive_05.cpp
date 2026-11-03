#include <utility>

enum Compass { east, west };

int main()
{
    std::pair<int, int> values{1, 2};
    auto [direction, value] = values;
    Compass dir = east;
    return direction + value + static_cast<int>(dir);
}
