#include <iostream>

int main() {
    int total = 1024;
    int shift = 3;
    int quotient = total >> shift;
    std::cout << quotient << '\n';
    return 0;
}
