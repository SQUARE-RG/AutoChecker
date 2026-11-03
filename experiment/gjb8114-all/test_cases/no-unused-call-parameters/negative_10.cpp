#include <iostream>

template <typename T>
class Accumulator {
public:
    T total{};

    void add(T value, int unused_scale) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-2]
        total += value;
    }

    T get() const { return total; }
};

int main() {
    Accumulator<int> acc;
    acc.add(3, 10);
    std::cout << acc.get() << std::endl;
    return 0;
}
