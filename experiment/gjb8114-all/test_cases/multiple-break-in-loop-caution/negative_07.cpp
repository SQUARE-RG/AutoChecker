#include <iostream>
#include <stdexcept>

int scan_until_error_or_marker(int limit) {
    int visited = 0;
    for (int i = 0; i < limit; ++i) {
        try {
            if (i == 3) {
                break;
            }
            if (i == 1) {
                throw std::runtime_error("synthetic failure");
            }
            ++visited;
        } catch (const std::runtime_error&) {
            break; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-2]
        }
    }
    return visited;
}

int main() {
    std::cout << scan_until_error_or_marker(10) << '\n';
    return 0;
}
