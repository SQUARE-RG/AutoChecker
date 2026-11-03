#include <iostream>

int main() {
    int sum = 0;
    for (int i = 0; i != 12; i += 3) {
        sum += i;
    }
    std::cout << sum << '\n';
    return 0;
}
