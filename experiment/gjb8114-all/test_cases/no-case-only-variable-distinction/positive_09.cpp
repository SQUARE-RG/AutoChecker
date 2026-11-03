#include <functional>

int main() {
    auto combine = [](int firstValue, int secondValue) { return firstValue + secondValue; };
    int result = combine(1, 2);
    return result;
}
