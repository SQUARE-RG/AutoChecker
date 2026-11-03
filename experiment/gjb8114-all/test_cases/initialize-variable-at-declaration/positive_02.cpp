#include <array>
#include <iostream>

int main() {
    std::array<int, 3> values{1, 2, 3};
    int* pointer = nullptr;
    if (pointer != nullptr) {
        std::cout << *pointer << std::endl;
    }
    std::cout << values[0] << std::endl;
    return 0;
}
