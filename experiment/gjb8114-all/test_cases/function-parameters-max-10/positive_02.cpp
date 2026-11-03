#include <iostream>

template <typename T>
T sumTenTemplate(T a1, T a2, T a3, T a4, T a5, T a6, T a7, T a8, T a9, T a10) {
    return a1 + a2 + a3 + a4 + a5 + a6 + a7 + a8 + a9 + a10;
}

int main() {
    std::cout << sumTenTemplate<int>(1, 2, 3, 4, 5, 6, 7, 8, 9, 10) << '\n';
    return 0;
}
