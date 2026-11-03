#include <utility>

void compute(void)
{
}

int main()
{
    auto [result, value] = std::pair<int, int>{0, 1};
    (void)value;
    return result;
}
