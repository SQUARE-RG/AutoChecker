#include <iostream>

int main() {
    int total = 29;
    int chunk = 5;
    int remaining = total;
    int count = 0;
    while (remaining / chunk > 0) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-2]
        remaining -= chunk;
        ++count;
    }
    std::cout << count << '\n';
    return 0;
}
