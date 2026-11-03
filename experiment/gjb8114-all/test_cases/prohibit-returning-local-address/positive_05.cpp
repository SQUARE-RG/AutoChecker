#include <iostream>

int globalArray[10] = {0};

int* getGlobalElement(int index) {
    return &globalArray[index];
}

int main() {
    int* p = getGlobalElement(2);
    std::cout << *p << std::endl;
    return 0;
}
