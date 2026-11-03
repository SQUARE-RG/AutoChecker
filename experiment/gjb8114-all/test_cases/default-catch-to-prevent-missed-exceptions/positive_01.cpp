#include <exception>
#include <stdexcept>

int main() {
    try {
        throw std::runtime_error("example");
    } catch (const std::exception&) {
        return 1;
    } catch (...) {
        return 2;
    }
    return 0;
}
