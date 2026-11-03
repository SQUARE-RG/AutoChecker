#include <cstdlib>
#include <iostream>

int main() {
    int status = std::system("exit 0"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-4]
    std::cout << "status=" << status << '\n';
    return 0;
}
