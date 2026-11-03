#include <string_view>

int add_numbers(int left, int right) { return left + right; }
int multiply_numbers(int left, int right) { return left * right; }

int compute(std::string_view operation, int left, int right) {
    if (operation == "add") {
        return add_numbers(left, right);
    }
    if (operation == "multiply") {
        return multiply_numbers(left, right);
    }
    return 0;
}

int main() {
    return compute("add", 2, 3);
}
