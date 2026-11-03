#include <cstdint>

struct LaunchState {
    int retryCount; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-13-1]
};

int main() {
    return 0;
}
