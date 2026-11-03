#include <cstring>

struct Buffer {
    char data[64] = "header";

    std::size_t remaining_capacity() const {
        std::size_t used = std::strlen(data);
        std::size_t total = sizeof(data);
        return used < total ? total - used - 1 : 0;
    }

    Buffer& operator+=(const char* tag) {
        std::strncat(data, tag, remaining_capacity());
        return *this;
    }
};

int main() {
    Buffer buffer;
    buffer += "!";
    return 0;
}
