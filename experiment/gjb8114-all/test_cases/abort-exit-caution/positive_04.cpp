#include <iostream>
#include <stdexcept>

class Buffer {
public:
    void require_non_empty(int size) const {
        if (size == 0) {
            throw std::invalid_argument("buffer must not be empty");
        }
    }
};

int main() {
    Buffer buffer;
    try {
        buffer.require_non_empty(0);
    } catch (const std::invalid_argument& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
    return 0;
}
