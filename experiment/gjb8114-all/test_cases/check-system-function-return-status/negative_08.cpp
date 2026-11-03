#include <cstdlib>
#include <tuple>

int main() {
    std::ignore = std::system("echo hello"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-4]
    return 0;
}
