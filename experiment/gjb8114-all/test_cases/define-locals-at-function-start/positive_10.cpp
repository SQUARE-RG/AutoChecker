#include <iostream>

template <typename T>
void report(T value) {
    T copy = value;
    if constexpr (sizeof(T) > 4) {
        std::cout << "large\n";
    } else {
        std::cout << "small\n";
    }
    std::cout << copy << '\n';
}

int main() {
    report(42);
    return 0;
}
