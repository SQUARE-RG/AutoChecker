#include <iostream>

int main() {
    int i = 0;
    int sum = 0;
    while (i < 10) {
        ++i;
        if (i % 2 == 0) {
            continue;
        }
        if (i % 3 == 0) {
            sum += i * 2;
        } else {
            sum += i;
        }
    }
    std::cout << sum << '\n';
    return 0;
}
