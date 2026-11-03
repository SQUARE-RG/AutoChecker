#include <iostream>
#include <optional>

int main() {
    try {
        throw std::optional<int>(7);
    } catch (const std::optional<int>& caught) {
        std::cout << (caught ? *caught : -1);
    }
    return 0;
}
