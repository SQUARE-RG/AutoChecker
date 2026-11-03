#include <cstdlib>
#include <iostream>

int main() {
    std::cout << std::system("echo hello") << '\n'; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-4]
    return 0;
}
