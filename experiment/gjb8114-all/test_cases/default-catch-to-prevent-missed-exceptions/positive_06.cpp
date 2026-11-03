#include <stdexcept>

void release_pointer(bool should_throw) {
    try {
        if (should_throw) {
            throw new std::runtime_error("allocated");
        }
    } catch (const std::runtime_error* e) {
        delete e;
    } catch (...) {
        // Prevent missed exceptions from escaping.
    }
}

int main() {
    release_pointer(true);
    return 0;
}
