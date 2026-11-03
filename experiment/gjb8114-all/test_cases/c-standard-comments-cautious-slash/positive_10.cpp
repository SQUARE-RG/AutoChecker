#include <iostream>

int main() {
    try {
        throw 42; /* throw sample integer error */
    } catch (int error) { /* handle integer exception */
        std::cout << error << std::endl;
    }
    return 0;
}
