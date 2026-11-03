#include <iostream>

int main() {
    unsigned int value = 0;
    std::cin >> value;
    if (value > 0) {
        value = 1u;
    } else {
        value = 2u;
    }
    return static_cast<int>(value);
}
