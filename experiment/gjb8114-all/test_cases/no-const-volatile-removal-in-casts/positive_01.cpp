#include <iostream>

int main() {
    int value = 5;
    const int* cp = const_cast<const int*>(&value);
    (void)cp;
    return 0;
}
