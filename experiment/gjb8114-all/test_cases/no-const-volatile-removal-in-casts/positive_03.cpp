#include <iostream>

int main() {
    const int value = 5;
    const int* cp = &value;
    const volatile int* cvp = const_cast<const volatile int*>(cp);
    std::cout << *cvp << '\n';
    return 0;
}
