#include <cstdint>

using UnaryFn = int (*)(int);

static int add_one(int x) {
    return x + 1;
}

static int add_two(int x) {
    return x + 2;
}

static int apply(UnaryFn fn, int value) {
    return fn(value);
}

int main() {
    int result = apply(&add_one, 1);
    result = apply(&add_two, result);
    return result;
}
