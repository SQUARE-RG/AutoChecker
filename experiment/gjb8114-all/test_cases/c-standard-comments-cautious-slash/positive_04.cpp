#include <iostream>

/*
 * 描述一个简单的点结构：
 * 使用块注释书写多行说明，避免双斜杠注释。
 */
struct Point
{
    int x;
    int y;
}; /* 结构体定义结束 */

static int sum_coords(const Point& p)
{
    return p.x + p.y;
}

int main()
{
    Point origin{0, 0};
    /* std::cout << "debug" << std::endl; */
    std::cout << sum_coords(origin) << std::endl; /* 输出坐标和 */
    return 0;
}
