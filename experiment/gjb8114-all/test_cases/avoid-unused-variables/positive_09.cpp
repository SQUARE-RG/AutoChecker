#include <vector>

int main() {
    std::vector<int> values{1, 2, 3, 4};
    int sum = 0;
    for (const auto& item : values) {
        sum += item;
    }
    return sum;
}
