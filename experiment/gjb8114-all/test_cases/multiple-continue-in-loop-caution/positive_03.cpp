#include <iostream>

int main() {
    int total = 0;
    for (int i = 0; i < 10; ++i) {
        if (i == 5) {
            continue;
        }
        if (i % 2 == 0) {
            total += i;
        } else {
            total += i * 2;
        }
    }
    std::cout << total << std::endl;
    return 0;
}
