#include <cstdint>

constexpr int constexpr_sum_small() {
    int total = 0;
    total += 1;
    total += 2;
    return total;
}

int main() {
    int result = constexpr_sum_small();
    (void)result;
    return 0;
}
