#include <iostream>

void check(int x) {
    if (x > 0) {
        int a = 0;
        int b = 0;
        a = x;
        b = a + 1;
        throw b;
    }
}

int main() {
    try {
        check(2);
    } catch (int value) {
        std::cout << value << std::endl;
    }
    return 0;
}
