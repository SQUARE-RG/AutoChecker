#include <iostream>

int main() {
    int *p = new int[0];
    if (p != nullptr) {
        std::cout << "allocated" << std::endl;
    }
    delete[] p;
    return 0;
}
