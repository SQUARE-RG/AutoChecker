#include <iostream>
#include <stdexcept>

int main() {
    try {
        throw std::logic_error("invalid operation");
    } catch (...) {
        std::cout << "caught non-pointer exception\n";
    }
    return 0;
}
