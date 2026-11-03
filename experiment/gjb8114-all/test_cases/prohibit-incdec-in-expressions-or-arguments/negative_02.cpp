#include <iostream>

int twice(int v) {
    return v * 2;
}

int main() {
    int x = 5;
    int y = twice(++x); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-5]
    std::cout << y << std::endl;
    return 0;
}
