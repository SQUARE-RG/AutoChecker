#include <array>
#include <iostream>

int main() {
    try {
        throw std::array<int, 3>{1, 2, 3};
    } catch (const std::array<int, 3>& caught) {
        std::cout << caught[0];
    }
    return 0;
}
