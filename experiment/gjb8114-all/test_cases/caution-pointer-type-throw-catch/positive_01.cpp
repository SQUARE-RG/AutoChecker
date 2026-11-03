#include <iostream>

int main() {
    try {
        throw 42;
    } catch (int e) {
        std::cout << e << std::endl;
    }
    return 0;
}
