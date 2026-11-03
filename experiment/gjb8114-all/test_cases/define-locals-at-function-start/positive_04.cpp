#include <iostream>
#include <vector>
#include <algorithm>

int main() {
    std::vector<int> values{1, 2, 3, 4};
    int sum = 0;
    std::for_each(values.begin(), values.end(), [&sum](int v) {
        int doubled = v * 2;
        int unused = 0;
        sum += doubled;
        sum += unused;
    });
    std::cout << sum << '\n';
    return 0;
}
