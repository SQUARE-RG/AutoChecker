#include <iostream>

int main() {
    int sum = 0;
    int i = 0;
    while (i < 10) {
        sum += i;
        ++i;
    }
    std::cout << sum << std::endl;
    return 0;
}
