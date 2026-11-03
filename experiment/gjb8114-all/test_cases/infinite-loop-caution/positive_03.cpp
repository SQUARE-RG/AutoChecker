#include <array>
#include <iostream>

int main() {
    const std::array<int, 5> values{1, 2, 3, 4, 5};
    int sum = 0;
    for (int value : values) {
        sum += value;
    }
    std::cout << sum << '\n';
    return 0;
}
