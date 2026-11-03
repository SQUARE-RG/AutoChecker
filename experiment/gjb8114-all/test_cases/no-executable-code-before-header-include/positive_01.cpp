// 遵循场景：头文件位于文件顶部，任何可执行代码之前。
#include <iostream>

int main()
{
    int ix = 0;
    int iy = 1;
    int iz = 2;
    int idata = ix + iy + iz;
    std::cout << idata << '\n';
    return 0;
}
