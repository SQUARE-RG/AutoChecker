#include <iostream>

int compute(int value) {
    return value + 10;
}

int main() {
    int x = 3;
    int i = 0;
    do {
        ++x;
        ++i;
    } while (i < 3);
    --x;
    int result = compute(42);
    std::cout << result << " " << x << std::endl;
    return 0;
}
