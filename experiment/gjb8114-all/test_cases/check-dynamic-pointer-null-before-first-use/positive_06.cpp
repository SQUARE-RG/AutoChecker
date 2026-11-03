#include <iostream>
#include <new>

int main() {
    int *counter = new (std::nothrow) int(0);
    if (counter == nullptr) {
        return -1;
    }
    *counter += 5;
    std::cout << *counter << '\n';
    delete counter;
    return 0;
}
