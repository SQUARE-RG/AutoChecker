#include <array>

int sum3(const std::array<int, 3>& values) {
    return values[0] + values[1] + values[2];
}

int main() {
    const std::array<int, 3> values{1, 2, 3};
    return sum3(values) == 6 ? 0 : 1;
}
