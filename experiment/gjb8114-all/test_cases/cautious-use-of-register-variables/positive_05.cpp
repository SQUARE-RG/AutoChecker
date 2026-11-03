#include <iostream>

int main() {
    int sum = 0;
    if (sum == 0) {
        const int offset = 3;
        sum += offset;
    }
    std::cout << sum << std::endl;
    return 0;
}
