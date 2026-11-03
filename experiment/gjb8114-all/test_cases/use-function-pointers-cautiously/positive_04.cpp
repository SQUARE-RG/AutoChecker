#include <iostream>

class Calculator {
public:
    int addOne(int value) const { return value + 1; }
    int twice(int value) const { return value * 2; }
};

int main() {
    Calculator calculator;
    int input = 5;
    int first = calculator.addOne(input);
    int second = calculator.twice(input);
    std::cout << first << ' ' << second << '\n';
    return 0;
}
