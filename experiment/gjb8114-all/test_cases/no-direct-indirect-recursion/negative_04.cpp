#include <functional>
#include <iostream>

int main() {
    std::function<int(int)> factorial;
    factorial = [&factorial](int n) -> int {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-16]
    };

    std::cout << factorial(5) << '\n';
    return 0;
}
