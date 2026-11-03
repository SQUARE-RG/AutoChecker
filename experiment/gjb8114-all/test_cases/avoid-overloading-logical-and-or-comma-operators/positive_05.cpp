#include <iostream>

int main() {
    int data[5] = {1, 2, 3, 4, 5};
    int sum = 0;
    for (int i = 0, n = 5; i < n; ++i) {
        sum += data[i];
    }
    std::cout << sum << '\n';
    return 0;
}
