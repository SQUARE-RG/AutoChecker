#include <iostream>

int find_secret(int limit) {
    int found = -1;
    for (;;) {
        if (limit <= 0) {
            break;
        }
        if (limit % 2 == 0) {
            limit /= 2;
            continue;
        }
        if (limit % 3 == 0) {
            limit -= 1;
            continue; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-3]
        }
        found = limit;
        break;
    }
    return found;
}

int main() {
    std::cout << find_secret(12) << std::endl;
    return 0;
}
