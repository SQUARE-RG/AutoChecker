#include <iostream>

template <typename T>
class Accumulator {
public:
    T total{};

    void add(T value, int scale) {
        total += value * static_cast<T>(scale);
    }

    T get() const { return total; }
};

int main() {
    Accumulator<int> acc;
    acc.add(3, 10);
    std::cout << acc.get() << std::endl;
    return 0;
}
