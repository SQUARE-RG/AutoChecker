#include <iostream>

int main() {
    int value = 42;
    int* ptr = &value;
    try {
        throw ptr;
    } catch (int*) {
        std::cout << "int pointer caught" << std::endl;
    }
    return 0;
}
