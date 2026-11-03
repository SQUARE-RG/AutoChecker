#include <iostream>

struct IncrementPolicy {
    static int apply(int value) {
        return value + 1;
    }
};

template <typename Policy>
int apply_operation(int value) {
    return Policy::apply(value);
}

int main() {
    int result = apply_operation<IncrementPolicy>(4);
    std::cout << result << std::endl;
    return 0;
}
