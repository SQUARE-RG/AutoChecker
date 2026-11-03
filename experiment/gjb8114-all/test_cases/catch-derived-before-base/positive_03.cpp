#include <iostream>
#include <exception>
#include <stdexcept>

int main() {
    try {
        throw std::runtime_error("runtime error");
    }
    catch (const std::runtime_error& e) {
        std::cout << "runtime_error: " << e.what() << std::endl;
    }
    catch (const std::exception& e) {
        std::cout << "exception: " << e.what() << std::endl;
    }
    return 0;
}
