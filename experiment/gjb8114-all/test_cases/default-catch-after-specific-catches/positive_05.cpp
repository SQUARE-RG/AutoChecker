#include <iostream>
#include <exception>
#include <stdexcept>

int main() {
    try {
        throw std::runtime_error("x");
    }
    catch (const std::exception& e) {
        std::cout << e.what() << std::endl;
    }
    catch (const char* msg) {
        std::cout << msg << std::endl;
    }
    catch (...) {
        std::cout << "unknown" << std::endl;
    }
    return 0;
}
