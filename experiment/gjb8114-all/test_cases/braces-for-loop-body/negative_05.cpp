#include <iostream>
int main() {
    int sum = 0;
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-1]
            sum += i * j;
    }
    std::cout << sum << std::endl;
    return 0;
}
