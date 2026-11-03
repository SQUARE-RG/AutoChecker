#include <iostream>

void display(const int (&arr)[10]) {
    for (int i = 0; i < 10; ++i) {
        std::cout << arr[i] << ' ';
    }
    std::cout << std::endl;
}

int main() {
    int values[10] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
    display(values);
    return 0;
}
