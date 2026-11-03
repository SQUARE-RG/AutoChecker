#include <iostream>

int main() {
    int arr[] = {1, -2, 0, 3};
    int sum = 0;
    for (int x : arr) {
        if (x < 0) {
            continue;
        }
        if (x > 0) {
            sum += x;
        }
    }
    std::cout << sum << '\n';
    return 0;
}
