#include <iostream>

int main() {
    int value = 0;
    std::cin >> value;
    if (value >= 0) {
        value = 1;
    } else {
        value = 2;
    }
    return value;
}
