#include <cstdlib>

int main() {
    auto f = [](int value1, int label) {
        return value1 + label;
    };
    return f(0, 1);
}
