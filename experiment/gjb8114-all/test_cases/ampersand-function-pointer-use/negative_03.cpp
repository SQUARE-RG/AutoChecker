#include <cstdlib>

int fun(int a, int b);

int main() {
    if (nullptr == fun) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-2]
        return -1;
    }
    return 0;
}

int fun(int a, int b) {
    return a - b;
}
