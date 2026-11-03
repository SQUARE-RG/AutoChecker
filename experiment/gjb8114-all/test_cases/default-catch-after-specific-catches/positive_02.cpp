#include <iostream>
#include <stdexcept>

int main() {
    try {
        try {
            throw std::runtime_error("inner");
        } catch (const std::exception& e) {
            std::cout << "inner std exception: " << e.what() << "\n";
        } catch (...) {
            std::cout << "inner default\n";
        }
    } catch (...) {
        std::cout << "outer default\n";
    }
    return 0;
}
