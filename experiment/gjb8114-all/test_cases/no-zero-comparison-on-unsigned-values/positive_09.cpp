#include <iostream>

int main() {
    unsigned int u = 10;
    int count = 0;
    do {
        ++count;
    } while (u < 100u && count < 3);
    std::cout << u << '\n';
    return 0;
}
