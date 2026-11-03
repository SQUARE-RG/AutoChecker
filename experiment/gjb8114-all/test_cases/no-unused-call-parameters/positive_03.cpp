#include <iostream>

template <typename T>
T combine(T first, T second) {
    return first + second;
}

int main() {
    std::cout << combine(2, 3) << std::endl;
    return 0;
}
