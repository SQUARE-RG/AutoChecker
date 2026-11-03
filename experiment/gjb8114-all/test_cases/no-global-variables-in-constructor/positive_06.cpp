#include <iostream>

int gSeed = 3;

class Accumulator {
public:
    explicit Accumulator(int n);
    int total_value() const;
private:
    int total;
};

Accumulator::Accumulator(int n) {
    total = 0;
    for (int i = 0; i < n; ++i) {
        total += 1;
    }
}

int Accumulator::total_value() const { return total; }

int main() {
    Accumulator acc(gSeed);
    std::cout << acc.total_value() << std::endl;
    return 0;
}
