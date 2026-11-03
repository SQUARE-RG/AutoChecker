#include <iostream>

void releaseScalar() {
    int* value = new int(42);
    std::cout << *value << '\n';
    delete value;
    value = nullptr;
}

int main() {
    releaseScalar();
    return 0;
}
