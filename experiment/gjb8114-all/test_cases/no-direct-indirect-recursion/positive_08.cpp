#include <cstdint>

static int leaf(int x) {
    return x + 1;
}

static int middle(int x) {
    return leaf(x) * 2;
}

static int outer(int x) {
    return middle(x) - 1;
}

int main() {
    return outer(3);
}
