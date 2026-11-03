#include <iostream>

int main() {
    int mode = 2;
    switch (mode) {
        case 1: {
            int value = 10;
            std::cout << value << std::endl;
            break;
        }
        case 2: {
            std::cout << "mode 2" << std::endl;
            break;
        }
        default:
            break;
    }
    return 0;
}
