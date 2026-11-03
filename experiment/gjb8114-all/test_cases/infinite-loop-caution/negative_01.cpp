#include <iostream>

int main() {
    int counter = 0;
    while (true) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-1]
        ++counter;
        std::cout << counter << std::endl;
        if (counter >= 5) {
            break;
        }
    }
    return 0;
}
