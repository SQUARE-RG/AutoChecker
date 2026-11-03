#include <iostream>

int main() {
    int count = 3;
    while (count > 0) {
        int localCount = count;
        --localCount;
        --count;
    }
    std::cout << count << '\n';
    return 0;
}
