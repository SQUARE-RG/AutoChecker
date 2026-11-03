#include <cstdlib>

int main() {
    std::system("mkdir -p /tmp/ucasaat_demo"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-4]
    return 0;
}
