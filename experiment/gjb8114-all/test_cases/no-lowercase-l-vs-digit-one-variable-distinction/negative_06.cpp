#include <utility>

int main() {
    std::pair<int, int> p{0, 1};
    auto [fSpeedl, fSpeed1] = p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-9]
    return fSpeedl + fSpeed1;
}
