#include <iostream>
struct BaseError {
    virtual ~BaseError() = default;
    virtual int code() const { return 1; }
};
struct DerivedError : BaseError {
    int code() const override { return 2; }
};
int main() {
    try {
        throw DerivedError{};
    } catch (const BaseError &e) {
        std::cout << e.code();
    }
    return 0;
}
