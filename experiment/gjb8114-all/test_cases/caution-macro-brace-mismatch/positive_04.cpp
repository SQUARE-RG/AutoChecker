#include <iostream>

#define PRINT_SIGN(x) if ((x) >= 0) { std::cout << "non-negative\n"; } else { std::cout << "negative\n"; }

int main() {
    int value = -5;
    PRINT_SIGN(value)
    return 0;
}
