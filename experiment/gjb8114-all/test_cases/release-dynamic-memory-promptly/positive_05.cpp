#include <cstdlib>
#include <iostream>

int main() {
    int* buffer = static_cast<int*>(std::calloc(8, sizeof(int)));
    if (buffer == nullptr) {
        return 1;
    }
    buffer[0] = 7;
    std::cout << buffer[0];
    std::free(buffer);
    return 0;
}
