#include <cstdint>

void spinForever() {
    volatile std::uint64_t counter = 0;
    while (true) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-1]
        counter = counter + 1;
    }
}

int main() {
    spinForever();
    return 0;
}
