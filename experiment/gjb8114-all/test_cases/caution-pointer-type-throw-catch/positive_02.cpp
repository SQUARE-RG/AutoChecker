#include <iostream>

struct Error {
    int code;
};

int main() {
    try {
        throw Error{5};
    } catch (const Error& e) {
        std::cout << e.code << std::endl;
    }
    return 0;
}
