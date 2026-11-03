#include <iostream>

void printArray(const int values[4]) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-1]
{
    for (int i = 0; i < 4; ++i) {
        std::cout << values[i] << ' ';
    }
    std::cout << std::endl;
}

int main() {
    int data[4] = {1, 2, 3, 4};
    printArray(data);
    return 0;
}
