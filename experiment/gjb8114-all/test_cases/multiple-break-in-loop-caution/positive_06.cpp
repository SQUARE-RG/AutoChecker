#include <iostream>

int main() {
    for (int i = 0; i < 10; ++i) {
        if (i % 2 == 0) {
            continue;
        }
        if (i > 6) {
            break;
        }
        std::cout << i << '\n';
    }
    return 0;
}
