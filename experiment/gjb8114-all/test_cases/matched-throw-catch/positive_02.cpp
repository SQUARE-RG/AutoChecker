#include <exception>
#include <iostream>
#include <stdexcept>

int main() {
    try {
        throw std::runtime_error("error");
    } catch (const std::exception &e) {
        std::cout << e.what() << std::endl;
    }
    return 0;
}
