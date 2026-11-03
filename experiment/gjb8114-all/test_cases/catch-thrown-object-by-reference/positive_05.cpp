#include <iostream>

struct Error {
    int code;
};

int main() {
    try {
        throw Error{42};
    }
    catch (Error &e) {
        std::cout << e.code << std::endl;
    }
    return 0;
}
