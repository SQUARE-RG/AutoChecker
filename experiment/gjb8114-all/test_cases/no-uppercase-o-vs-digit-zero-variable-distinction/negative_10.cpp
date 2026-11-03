// negative_10.cpp
#include <utility>

int main() {
    auto [fSpeedO, fSpeed0] = std::make_pair(1, 2); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-10]
    return fSpeedO + fSpeed0;
}
