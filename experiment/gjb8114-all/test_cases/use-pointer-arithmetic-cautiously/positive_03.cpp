#include <iostream>
#include <vector>

int sum_values(const std::vector<int>& values) {
    int total = 0;
    for (int value : values) {
        total += value;
    }
    return total;
}

int main() {
    std::vector<int> values = {1, 2, 3, 4, 5};
    std::cout << sum_values(values) << '\n';
    return 0;
}
