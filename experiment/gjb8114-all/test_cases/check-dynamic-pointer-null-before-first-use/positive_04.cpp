#include <cstdlib>
#include <iostream>

int main() {
    int* data = static_cast<int*>(std::calloc(1, sizeof(int)));
    if (data != nullptr) {
        std::cout << *data;
    } else {
        return 1;
    }
    std::free(data);
    return 0;
}
