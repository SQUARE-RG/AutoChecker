#include <functional>
#include <iostream>

int main() {
    std::logical_and<bool> land;
    std::logical_or<bool> lor;

    bool first = land(true, false);
    bool second = lor(first, true);
    std::cout << second << '\n';
    return 0;
}
