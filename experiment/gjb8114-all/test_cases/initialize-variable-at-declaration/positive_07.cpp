#include <iostream>

enum class Mode { Off, On };

int main() {
    Mode mode = Mode::Off;

    if (mode == Mode::On) {
        std::cout << 1 << std::endl;
    } else {
        std::cout << 0 << std::endl;
    }

    return 0;
}
