#include <setjmp.h>
#include <iostream>

jmp_buf error_mark;

double divide(double numerator, double denominator) {
    return numerator / denominator;
}

int main() {
    double a = 1.0;
    double b = 0.0;
    if (setjmp(error_mark) == 0) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-2]
        std::cout << divide(a, b) << '\n';
    } else {
        std::cout << "division failed\n";
    }
    return 0;
}
