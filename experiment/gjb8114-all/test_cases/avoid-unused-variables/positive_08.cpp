#include <iostream>
#include <stdexcept>

int main() {
    try {
        int value = 7;
        std::cout << value << '\n';
    } catch (const std::exception& e) {
        std::cout << e.what() << '\n';
    }
    return 0;
}
