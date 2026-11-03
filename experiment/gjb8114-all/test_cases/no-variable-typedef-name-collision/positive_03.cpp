#include <iostream>

typedef int (*BinaryOp)(int, int);

int add(int a, int b) {
    return a + b;
}

int main() {
    BinaryOp operation = add;
    std::cout << operation(4, 5) << std::endl;
    return 0;
}
