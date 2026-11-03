#include <memory>
#include <iostream>

int main() {
    std::unique_ptr<int> owner(new int(42));
    int* raw = owner.release();
    std::cout << *raw << '\n';
    delete raw;
    return 0;
}
