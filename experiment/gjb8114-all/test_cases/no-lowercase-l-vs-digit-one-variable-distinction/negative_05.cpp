#include <cstdlib>

int main() {
    auto f = [](int fSpeedl, int fSpeed1) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-9]
        return fSpeedl + fSpeed1;
    };
    return f(0, 1);
}
