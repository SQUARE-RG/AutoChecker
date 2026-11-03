#include <iostream>

int main() {
    int status = 3;
    if (status == 3) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-12-1]
        std::cout << "match\n";
    }
    return 0;
}
