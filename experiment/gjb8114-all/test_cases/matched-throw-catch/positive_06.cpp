#include <exception>
#include <stdexcept>

int main() {
    try {
        try {
            throw 42;
        } catch (int) {
        }
        throw std::runtime_error("boom");
    } catch (const std::exception&) {
    }
    return 0;
}
