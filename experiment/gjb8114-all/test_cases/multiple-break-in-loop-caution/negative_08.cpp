#include <iostream>

int adjust_and_exit(int value) {
    int steps = 0;
    do {
        if (value < 0) {
            break;
        }
        value -= 2;
        ++steps;
        break; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-2]
    } while (value > 0);
    return steps;
}

int main() {
    std::cout << adjust_and_exit(7) << '\n';
    return 0;
}
