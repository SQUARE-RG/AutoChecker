#include <cstdlib>

int main() {
    bool fatal_error = true;
    if (fatal_error) {
        std::abort(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-3]
    }
    return 0;
}
