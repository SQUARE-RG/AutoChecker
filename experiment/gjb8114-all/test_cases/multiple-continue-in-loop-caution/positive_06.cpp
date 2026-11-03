#include <iostream>

int first_even_divisor(int value) {
    int divisor = 1;
    for (;;) {
        ++divisor;
        if (divisor > value) {
            break;
        }
        if (value % divisor == 0 && divisor % 2 == 0) {
            continue;
        }
        if (divisor >= value) {
            break;
        }
    }
    return divisor;
}

int main() {
    std::cout << first_even_divisor(10) << std::endl;
    return 0;
}
