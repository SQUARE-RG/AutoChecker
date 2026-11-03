#include <cstdlib>

void cleanup() {
    static_cast<void>(std::system("rm -f /tmp/ucasaat_demo")); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-4]
}

int main() {
    cleanup();
    return 0;
}
