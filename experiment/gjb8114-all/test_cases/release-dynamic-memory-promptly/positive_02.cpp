#include <cstdlib>

void fill() {
    int* buffer = static_cast<int*>(std::malloc(10 * sizeof(int)));
    if (buffer != nullptr) {
        buffer[0] = 42;
        std::free(buffer);
    }
}

int main() {
    fill();
    return 0;
}
