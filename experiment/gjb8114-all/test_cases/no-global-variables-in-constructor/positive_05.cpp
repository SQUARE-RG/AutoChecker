#include <iostream>

int gBase = 4;

class Calculator {
public:
    explicit Calculator(int input);
    int result() const;
private:
    static int compute(int v);
    int value;
};

int Calculator::compute(int v) {
    return v * 2;
}

Calculator::Calculator(int input) : value(compute(input)) {}

int Calculator::result() const { return value; }

int main() {
    Calculator c(gBase);
    std::cout << c.result() << std::endl;
    return 0;
}
