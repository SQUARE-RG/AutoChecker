#include <iostream>

int main() {
    volatile int value = 7;
    volatile int& vref = value;
    const volatile int& cvref = const_cast<const volatile int&>(vref);
    std::cout << cvref << '\n';
    return 0;
}
