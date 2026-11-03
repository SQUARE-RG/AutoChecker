#include <iostream>
#include <numeric>
#include <vector>

class Accumulator {
public:
    int total(const std::vector<int>& values) const {
        return std::accumulate(values.begin(), values.end(), 0);
    }
};

int main() {
    Accumulator accumulator;
    std::vector<int> values{1, 2, 3, 4};
    std::cout << accumulator.total(values) << '\n';
    return 0;
}
