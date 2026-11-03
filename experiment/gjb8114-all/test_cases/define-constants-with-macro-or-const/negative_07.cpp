#include <iostream>
#include <cstdlib>

bool isOverThreshold(int value) {
    if (value >= 100) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-6]
        return true;
    }
    return false;
}

int main(int argc, char**) {
    int sample = argc;
    std::cout << isOverThreshold(sample) << std::endl;
    return EXIT_SUCCESS;
}
