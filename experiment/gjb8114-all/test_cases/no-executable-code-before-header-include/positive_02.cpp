// 遵循场景：所有头文件都在文件顶部，且其前不存在任何可执行代码。
#include <cstddef>
#include <iostream>

struct Point
{
    int x;
    int y;
};

constexpr int area(const Point& p)
{
    return p.x * p.y;
}

int main()
{
    Point p{4, 5};
    std::size_t bytes = sizeof(Point);
    std::cout << area(p) << ' ' << bytes << '\n';
    return 0;
}
