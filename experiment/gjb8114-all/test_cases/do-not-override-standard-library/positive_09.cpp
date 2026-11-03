#include <iostream>

int clamp_value(int value, int low, int high) {
    if (value < low) {
        return low;
    }
    if (value > high) {
        return high;
    }
    return value;
}

int main() {
    int result = clamp_value(15, 0, 10);
    std::cout << result << '\n';
    return result == 10 ? 0 : 1;
}
