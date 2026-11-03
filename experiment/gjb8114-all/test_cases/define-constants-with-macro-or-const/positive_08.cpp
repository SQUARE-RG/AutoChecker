#include <cstdlib>

const unsigned int kReadFlag = 0x04u;

unsigned int hasReadFlag(unsigned int flags) {
    return flags & kReadFlag;
}

int main(int argc, char**) {
    unsigned int sample = static_cast<unsigned int>(argc);
    return hasReadFlag(sample) ? EXIT_SUCCESS : EXIT_FAILURE;
}
