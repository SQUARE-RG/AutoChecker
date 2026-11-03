#include <exception>
#include <iostream>

int main() {
    int value = 0;
    try {
        if (value != 0) {
            value = 10;
        }
    } catch (const std::exception&) {
        value = -1;
    }
    std::cout << value << '\n';
    return 0;
}
