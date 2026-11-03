#include <iostream>

int compute(int value) {
    int result = 0;
    if (value < 0) {
        goto invalid;
    }
    result = value * 2;
    return result;

invalid:
    std::cout << "invalid value\n";
    return -1;
}

int main() {
    std::cout << compute(-3) << '\n';
    std::cout << compute(5) << '\n';
    return 0;
}
