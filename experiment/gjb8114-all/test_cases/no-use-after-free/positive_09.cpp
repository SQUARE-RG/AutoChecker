#include <vector>

int main()
{
    std::vector<int> values{1, 2, 3};
    int* data = values.data();

    int result = data[0];
    (void)result;

    values = std::vector<int>{4, 5, 6};
    return 0;
}
