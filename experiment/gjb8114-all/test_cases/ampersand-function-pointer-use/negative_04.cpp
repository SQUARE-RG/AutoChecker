#include <cstdlib>

int fun(int a, int b);

int main() {
    int (*p)(int, int) = nullptr;
    int x = 3;
    int y = 1;
    p = fun; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-2]
    return p(x, y);
}

int fun(int a, int b) {
    return a - b;
}
