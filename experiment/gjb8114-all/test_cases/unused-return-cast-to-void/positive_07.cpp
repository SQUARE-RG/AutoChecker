#include <functional>

int scale(int value)
{
    return value * 3;
}

int main()
{
    auto scaled = std::bind(scale, 14);
    (void)scaled();
    return 0;
}
