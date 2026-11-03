#include <iostream>

#define LOG_VALUE(x) do { std::cout << (x) << '\n'; } while (0)

int main() {
    int value = 42;
    if (value > 0)
        LOG_VALUE(value);
    else
        LOG_VALUE(0);
    return 0;
}
