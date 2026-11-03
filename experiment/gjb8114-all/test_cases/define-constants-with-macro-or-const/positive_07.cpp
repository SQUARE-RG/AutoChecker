#include <iostream>
#include <cstdlib>

const int kOverThreshold = 100;

bool isOverThreshold(int value) {
    if (value >= kOverThreshold) {
        return true;
    }
    return false;
}

int main(int argc, char**) {
    int sample = argc;
    std::cout << isOverThreshold(sample) << std::endl;
    return EXIT_SUCCESS;
}
