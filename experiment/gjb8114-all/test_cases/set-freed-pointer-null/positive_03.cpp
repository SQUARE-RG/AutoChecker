#include <iostream>

int main() {
    int* p = new int(42);
    *p = *p + 1;
    delete p;
    p = nullptr;
    return 0;
}
