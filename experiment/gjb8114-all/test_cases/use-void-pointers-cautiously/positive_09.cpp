#include <iostream>

int main() {
    int value = 42;
    int* pointer = &value;
    int** handle = &pointer;
    int* typed = *handle;
    std::cout << *typed << '\n';
    return 0;
}
