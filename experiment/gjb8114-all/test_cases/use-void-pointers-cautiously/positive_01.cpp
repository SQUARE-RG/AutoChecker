// Positive case 1: data is passed through a strongly typed pointer.
#include <iostream>

void printInt(const int* value) {
    if (value != nullptr) {
        std::cout << *value << '\n';
    }
}

int main() {
    int number = 7;
    printInt(&number);
    return 0;
}
