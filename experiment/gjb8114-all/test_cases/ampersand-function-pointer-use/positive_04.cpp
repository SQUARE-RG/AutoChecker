#include <cstdlib>

int fun(int a, int b);

int main() {
    int (*p)(int, int) = nullptr;
    int x = 3;
    int y = 1;
    p = &fun;
    return p(x, y);
}

int fun(int a, int b) {
    return a - b;
}
