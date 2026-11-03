#include <cstdint>

static int red(int depth);
static int green(int depth);
static int blue(int depth);

static int red(int depth) {
    if (depth <= 0) {
        return 0;
    }
    return green(depth - 1);
}

static int green(int depth) {
    if (depth <= 0) {
        return 1;
    }
    return blue(depth - 1);
}

static int blue(int depth) {
    if (depth <= 0) {
        return 2;
    }
    return red(depth - 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-16]
}

int main() {
    return red(3);
}
