#include <vector>

int main()
{
    std::vector<int> values{1, 2, 3};
    auto transform = [/* lambda capture note: separate * and / characters */ &values](int value) {
        return value * 2 + static_cast<int>(values.size());
    };

    int result = transform(values.front());
    return result > 0 ? 0 : 1;
}
