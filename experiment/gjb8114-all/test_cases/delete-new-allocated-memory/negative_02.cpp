#include <iostream>

void leakArray() {
    int* values = new int[4];  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-6-1]
    for (int i = 0; i < 4; ++i) {
        values[i] = i + 1;
    }
    std::cout << values[0] << '\n';
}

int main() {
    leakArray();
    return 0;
}
