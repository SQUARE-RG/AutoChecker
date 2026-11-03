#include <iostream>

int main() {
    int counter = 0;
    for (; true; ) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-1]
        counter += 1;
        if (counter > 1000) {
            std::cout << counter << std::endl;
            counter = 0;
        }
    }
    return 0;
}
