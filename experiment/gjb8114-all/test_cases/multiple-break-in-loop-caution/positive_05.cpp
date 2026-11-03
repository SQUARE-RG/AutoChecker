#include <iostream>

int main() {
    int value = 0;
    for (;;) {
        ++value;
        if (value >= 5) {
            break;
        }
        std::cout << value << '\n';
    }
    return 0;
}
