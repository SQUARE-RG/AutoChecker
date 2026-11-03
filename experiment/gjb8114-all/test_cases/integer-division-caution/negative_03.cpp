#include <iostream>

void printAverage(int value) {
    std::cout << value << std::endl;
}

int main() {
    int total = 42;
    int count = 5;
    printAverage(total / count); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-2]
    return 0;
}
