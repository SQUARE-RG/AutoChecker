#include <iostream>
#include <numeric>
#include <vector>

int sum_values(const std::vector<int>& values) {
    return std::accumulate(values.begin(), values.end(), 0);
}

int main() {
    std::vector<int> values = {1, 2, 3, 4, 5};
    std::cout << sum_values(values) << '\n';
    return 0;
}
