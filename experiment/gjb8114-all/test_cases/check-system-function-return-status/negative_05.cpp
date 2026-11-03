#include <cstdlib>

int main() {
    const char* cmd = "echo hello";
    if (std::system(cmd), false) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-4]
        return 1;
    }
    return 0;
}
