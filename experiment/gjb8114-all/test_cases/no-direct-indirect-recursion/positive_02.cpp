#include <iostream>

class Accumulator {
public:
    int add(int a, int b) const {
        return a + b;
    }

    int twice(int a) const {
        return add(a, a);
    }
};

int main() {
    Accumulator acc;
    std::cout << acc.twice(7) << std::endl;
    return 0;
}
