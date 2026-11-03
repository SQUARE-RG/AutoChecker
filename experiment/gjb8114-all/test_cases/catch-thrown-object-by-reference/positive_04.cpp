#include <iostream>

struct ErrorA {
    int code = 1;
};

struct ErrorB {
    int code = 2;
};

void mayThrow(bool first) {
    if (first) {
        throw ErrorA{};
    } else {
        throw ErrorB{};
    }
}

int main() {
    volatile bool first = true;
    try {
        mayThrow(first);
    }
    catch (ErrorA& e) {
        std::cout << e.code << '\n';
    }
    catch (ErrorB& e) {
        std::cout << e.code << '\n';
    }
    return 0;
}
