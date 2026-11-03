#include <cstdint>

struct ConvertibleNumber {
    int value;
    operator int() const {
        int total = value;
        total += 1;
        total += 2;
        return total;
    }
};

int main() {
    ConvertibleNumber number{7};
    int result = number;
    (void)result;
    return 0;
}
