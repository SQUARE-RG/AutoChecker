#include <vector>
#include <cstddef>

int sumPositive(const std::vector<int>& values) {
    int sum = 0;
    std::size_t i = 0;
    int count = 0;
    do {
        if (values[i] > 0) {
            sum += values[i];
        }
        ++i;
    } while (i < values.size());
    count = static_cast<int>(i);
    return sum + count;
}

int main() {
    std::vector<int> values = {1, -2, 3};
    return sumPositive(values);
}
