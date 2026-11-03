#include <iostream>

int main() {
    unsigned int u = 42;
    if (u <= 100u) {
        std::cout << "within bound\n";
    }
    return 0;
}
