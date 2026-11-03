#include <iostream>
#include <cmath> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-2-3]

int main() {
    /* Compute a square root using the standard library. */
    double result = std::sqrt(16.0);
    std::cout << result << std::endl;
    return 0;
}
