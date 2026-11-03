#include <iostream>

int main() {
    int remaining = 1024;
    int steps = 0;
    while (remaining > 0) {
        remaining /= 2;
        ++steps;
    }
    std::cout << steps << '\n';
    return 0;
}
