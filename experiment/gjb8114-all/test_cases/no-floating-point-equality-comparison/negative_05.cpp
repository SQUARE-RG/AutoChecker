#include <iostream>

int main() {
    int count = 0;
    for (float x = 0.0f; x == 1.0f; x += 0.25f) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-3]
        ++count;
    }
    std::cout << count << '\n';
    return 0;
}
