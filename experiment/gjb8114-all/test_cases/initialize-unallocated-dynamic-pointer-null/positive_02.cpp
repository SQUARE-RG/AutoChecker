#include <cstdlib>

int main() {
    int *buffer{};
    buffer = static_cast<int *>(std::calloc(4, sizeof(int)));
    if (buffer != nullptr) {
        buffer[0] = 3;
        std::free(buffer);
    } else {
        return -1;
    }
    return 0;
}
