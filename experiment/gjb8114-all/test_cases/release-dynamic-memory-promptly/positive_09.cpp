#include <iostream>
#include <memory>

int main() {
    std::allocator<int> alloc;
    int* buffer = alloc.allocate(4);
    for (int i = 0; i < 4; ++i) {
        buffer[i] = i * 3;
    }
    int sum = 0;
    for (int i = 0; i < 4; ++i) {
        sum += buffer[i];
    }
    alloc.deallocate(buffer, 4);
    std::cout << sum << std::endl;
    return 0;
}
