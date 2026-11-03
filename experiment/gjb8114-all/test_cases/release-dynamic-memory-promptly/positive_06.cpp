#include <iostream>

int main() {
    int* value = new int(10);
    std::cout << *value;
    delete value;
    value = new int(20);
    std::cout << *value;
    delete value;
    return 0;
}
