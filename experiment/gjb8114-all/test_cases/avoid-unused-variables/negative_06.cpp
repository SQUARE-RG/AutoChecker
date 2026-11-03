#include <iostream>

int main() {
    auto compute = []() {
        int unused = 3; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-2]
        return 0;
    };
    std::cout << compute() << std::endl;
    return 0;
}
