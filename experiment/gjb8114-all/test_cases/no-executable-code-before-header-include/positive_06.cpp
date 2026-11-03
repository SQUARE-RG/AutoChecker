class Point
{
public:
    int x;
    int y;
};

#include <cstdint>

int main()
{
    Point p{1, 2};
    std::uint32_t total = static_cast<std::uint32_t>(p.x + p.y);
    return static_cast<int>(total);
}
