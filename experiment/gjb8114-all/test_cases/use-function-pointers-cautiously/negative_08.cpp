#include <iostream>

struct Calculator {
    int factor;

    int multiply(int value) const {
        return value * factor;
    }

    int add(int value) const {
        return value + factor;
    }
};

int main() {
    Calculator calc{3};
    int (Calculator::*operation)(int) const = &Calculator::multiply; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-1]
    int result = (calc.*operation)(7);
    std::cout << result << std::endl;
    return 0;
}
