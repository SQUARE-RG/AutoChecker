#include <cstdint>

int main() {
    std::int8_t acc = 0;
    for (std::int8_t i = 10; i > -10; i -= 5) {
        acc += i;
    }
    return acc;
}
