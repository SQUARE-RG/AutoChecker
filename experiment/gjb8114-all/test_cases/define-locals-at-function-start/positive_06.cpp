#include <iostream>

int compute(int value) {
    int adjusted = value * 4;
    try {
        std::cout << "start\n";
    } catch (...) {
        std::cout << "error\n";
    }
    return adjusted;
}

int main() {
    std::cout << compute(3) << '\n';
    return 0;
}
