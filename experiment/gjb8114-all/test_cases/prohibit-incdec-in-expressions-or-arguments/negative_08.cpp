#include <iostream>

int main() {
    int x = 1;
    bool flag = true;
    int result = flag ? ++x : x; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-5]
    std::cout << result << std::endl;
    return 0;
}
