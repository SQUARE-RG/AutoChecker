#include <iostream>

int main() {
    int count = 0;
    while (count < 2) {
        int step = 1;
        count += step;
    }
    std::cout << count << std::endl;
    return 0;
}
