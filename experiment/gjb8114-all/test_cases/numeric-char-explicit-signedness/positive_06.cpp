#include <array>
#include <iostream>

int main() {
    std::array<unsigned char, 4> values{};
    values[0] = 1;
    values[1] = 2;
    int sum = values[0] + values[1];
    std::cout << sum << '\n';
    return 0;
}
