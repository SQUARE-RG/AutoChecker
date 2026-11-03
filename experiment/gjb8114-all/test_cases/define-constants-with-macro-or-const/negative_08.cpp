#include <cstdlib>

unsigned int hasReadFlag(unsigned int flags) {
    return flags & 0x04u; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-6]
}

int main(int argc, char**) {
    unsigned int sample = static_cast<unsigned int>(argc);
    return hasReadFlag(sample) ? EXIT_SUCCESS : EXIT_FAILURE;
}
