// Positive case 2: generics are implemented with a type-safe template instead of void*.
#include <iostream>

template <typename T>
void printValue(const T& value) {
    std::cout << value << '\n';
}

int main() {
    int number = 7;
    printValue(number);
    double ratio = 3.5;
    printValue(ratio);
    return 0;
}
