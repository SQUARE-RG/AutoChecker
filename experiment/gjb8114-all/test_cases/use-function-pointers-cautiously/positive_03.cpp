#include <iostream>

enum class Operation { AddOne, Double };

int apply(Operation op, int value) {
    switch (op) {
        case Operation::AddOne:
            return value + 1;
        case Operation::Double:
            return value * 2;
    }
    return value;
}

int main() {
    int input = 4;
    int first = apply(Operation::AddOne, input);
    int second = apply(Operation::Double, input);
    std::cout << first << ' ' << second << '\n';
    return 0;
}
