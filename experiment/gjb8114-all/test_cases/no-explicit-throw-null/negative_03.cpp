#include <cstddef>

int main(int argc, char** argv) {
    (void)argv;
    try {
        if (argc > 1) {
            throw NULL; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-5]
        }
    } catch (...) {
    }
    return 0;
}
