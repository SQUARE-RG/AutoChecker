#include <iostream>
struct MyError {
    int code;
};
typedef MyError ErrorAlias;
int main() {
    try {
        throw MyError{7};
    } catch (const ErrorAlias &e) {
        std::cout << e.code;
    }
    return 0;
}
