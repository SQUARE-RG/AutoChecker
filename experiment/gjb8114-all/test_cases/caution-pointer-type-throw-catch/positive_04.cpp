#include <iostream>
#include <stdexcept>

int main() {
    try {
        throw std::out_of_range("index out of range");
    } catch (const std::out_of_range& error) {
        std::cout << error.what() << std::endl;
    }
    return 0;
}
