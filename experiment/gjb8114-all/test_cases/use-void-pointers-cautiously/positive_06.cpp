#include <functional>
#include <iostream>

int apply_twice(const std::function<int(int)>& f, int x) {
    return f(f(x));
}

int main() {
    auto increment = [](int n) { return n + 1; };
    std::cout << apply_twice(increment, 5) << '\n';
    return 0;
}
