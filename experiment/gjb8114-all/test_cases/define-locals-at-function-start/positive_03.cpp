#include <iostream>

int accumulate(int limit) {
    int total = 0;
    int i = 0;
    int step = 2;
    while (i < limit) {
        total += i;
        i += step;
    }
    return total;
}

int main() {
    int result = accumulate(10);
    std::cout << result << '\n';
    return 0;
}
