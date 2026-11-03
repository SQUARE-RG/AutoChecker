#include <initializer_list>

int sum(std::initializer_list<int> values)
{
    int total = 0;
    for (int value : values) {
        total += value;
    }
    return total;
}

int main()
{
    return sum({1, 2, 3});
}
