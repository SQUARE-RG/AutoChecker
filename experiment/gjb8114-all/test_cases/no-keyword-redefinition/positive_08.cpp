#include <array>

int main()
{
    std::array<int, 3> values{1, 2, 3};
    int total = 0;
    for (int item : values) {
        total += item;
    }
    return total;
}
