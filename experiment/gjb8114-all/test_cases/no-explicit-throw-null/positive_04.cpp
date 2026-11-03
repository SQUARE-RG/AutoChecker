#include <iostream>
#include <stdexcept>

void rethrow_example() {
    try {
        throw std::runtime_error("boom");
    } catch (const std::runtime_error&) {
        throw;
    }
}

int main() {
    try {
        rethrow_example();
    } catch (const std::exception& e) {
        std::cout << e.what() << '\n';
    }
    return 0;
}
