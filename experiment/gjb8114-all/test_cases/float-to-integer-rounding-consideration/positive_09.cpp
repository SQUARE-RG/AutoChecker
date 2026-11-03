#include <cmath>

int main() {
    double values[] = {3.14159, 2.71828};
    int ints[2];
    for (int i = 0; i < 2; ++i) {
        ints[i] = static_cast<int>(std::round(values[i]));
    }
    return ints[0];
}
