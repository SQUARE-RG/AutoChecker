#include <iostream>
#include <exception>

int handle(int mode) {
    int result = 0;
    try {
        if (mode == 0) {
            result = 10;
        } else if (mode == 1) {
            result = 20;
        } else {
            result = 30;
        }
    } catch (const std::exception&) {
        result = -1;
    }
    return result;
}

int main() {
    std::cout << handle(0) << '\n';
    return 0;
}
