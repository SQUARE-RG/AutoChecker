#include <array>
#include <iostream>

/*
 * Section comment using standard C-style delimiters.
 */
int main() {
    std::array<int, 3> values{1, 2, 3};
    int sum = 0;
    /* Accumulate values with a block comment inside the loop. */
    for (const int value : values) {
        sum += value;
    }
    std::cout << sum << std::endl;
    return sum == 6 ? 0 : 1;
}
