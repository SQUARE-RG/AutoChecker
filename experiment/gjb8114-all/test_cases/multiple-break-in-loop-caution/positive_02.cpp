#include <iostream>

int main() {
    int n = 20;
    int steps = 0;
    do {
        if (n % 3 == 0) {
            break;
        }
        n -= 2;
        ++steps;
    } while (n > 0);
    std::cout << steps << '\n';
    return 0;
}
