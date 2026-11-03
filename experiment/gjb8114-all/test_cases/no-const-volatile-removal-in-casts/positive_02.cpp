#include <iostream>

int main() {
    int value = 5;
    volatile int& vr = const_cast<volatile int&>(value);
    (void)vr;
    return 0;
}
