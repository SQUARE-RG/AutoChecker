#include <iostream>
#include <string_view>

int main() {
    std::string_view view = "hello";
    if (view == "hello") { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-12-1]
        std::cout << 1 << std::endl;
    }
    return 0;
}
