// 违规场景：在 #include 之前出现了可执行代码（全局变量的动态初始化，程序启动时执行）。
int runtimeSeed = []() { return 3; }();

int runtimeValue = runtimeSeed * 7;

#include <cstddef> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-3]

int main()
{
    std::size_t size = static_cast<std::size_t>(runtimeValue);
    return static_cast<int>(size) - 21;
}
