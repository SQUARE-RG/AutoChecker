#include <atomic>
#include <iostream>

int main() {
    int value = 42;
    std::atomic<int*> slot{&value};
    int* typed = slot.load();
    std::cout << *typed << '\n';
    return 0;
}
