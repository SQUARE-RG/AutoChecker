#include <iostream>

int main() {
    int table[5] = {1, 2, 3, 4, 5};
    int total = 0;

    for (int i = 0; i < 5; ++i) {
        total += table[i];
    }

    int attempt = 0;
    do {
        ++attempt;
        total += attempt;
    } while (attempt < 3);

    std::cout << total << std::endl;
    return 0;
}
