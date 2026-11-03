#include <iostream>

int main() {
    int processed = 0;
    do {
        std::cout << processed << '\n';
        ++processed;
        if (processed == 5) {
            break;
        }
    } while (true); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-1]
    return 0;
}
