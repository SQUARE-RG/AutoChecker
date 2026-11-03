#include <iostream>

/* A standard C-style comment describing the entry point. */
int main() {
    int total = 0; /* standard block comment after a declaration */
    for (int i = 1; i <= 5; ++i) {
        total += i;
    }
    std::cout << total << std::endl;
    return 0;
}
