#include <array>

std::array<int, 4> g_limits = {10, 20, 30, 40}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-2]

int main() {
    return g_limits[0];
}
