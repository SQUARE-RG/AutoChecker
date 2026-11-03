#include <iostream>

int main() {
    float step = 0.25f;
    float value = 1.0f;
    while (value != 0.0f) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-3]
        value -= step;
    }
    std::cout << value << '\n';
    return 0;
}
