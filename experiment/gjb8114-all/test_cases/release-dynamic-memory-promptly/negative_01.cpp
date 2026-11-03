#include <iostream>

void process() {
    int* values = new int[10]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-3]
    for (int i = 0; i < 10; ++i) {
        values[i] = i;
    }
    std::cout << values[0];
}

int main() {
    process();
    return 0;
}
