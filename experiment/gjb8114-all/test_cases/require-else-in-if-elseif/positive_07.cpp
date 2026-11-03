#include <iostream>

int classify(int value) {
    int result = 0;
    if (int doubled = value * 2; doubled > 18) {
        result = 1;
    } else if (int tripled = value * 3; tripled > 30) {
        result = 2;
    } else {
        result = 0;
    }
    return result;
}

int main() {
    std::cout << classify(7) << '\n';
    return 0;
}
