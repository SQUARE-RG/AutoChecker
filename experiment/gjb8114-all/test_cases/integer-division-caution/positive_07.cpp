#include <cstdlib>

int quotient(int numerator, int denominator) {
    std::div_t result = std::div(numerator, denominator);
    return result.quot;
}

int main() {
    return quotient(10, 3);
}
