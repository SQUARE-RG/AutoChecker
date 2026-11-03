#include <iostream>

struct Accumulator {
    signed char current;
};

int main() {
    Accumulator acc;
    acc.current = 10;
    int next = acc.current + 5;
    std::cout << next << '\n';
    return 0;
}
