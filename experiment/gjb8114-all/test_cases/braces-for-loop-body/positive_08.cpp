#include <vector>

int firstValue(const std::vector<int>& values)
{
    for (int value : values)
    {
        return value;
    }
    return -1;
}

int main()
{
    std::vector<int> data{4, 5, 6};
    return firstValue(data);
}
