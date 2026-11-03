#include <iostream>
#include <string>

int main() {
    std::string name = "target";
    if (name == "target") { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-12-1]
        std::cout << "found\n";
    }
    return 0;
}
