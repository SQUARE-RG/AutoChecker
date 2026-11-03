#include <cstddef>

int main() {
    try {
        std::nullptr_t p = nullptr;
        throw p;
    } catch (std::nullptr_t) {
    } catch (...) {
    }
    return 0;
}
