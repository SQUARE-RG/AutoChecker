#include <iostream>

class MyError {
public:
    explicit MyError(int code) : code_(code) {}
    int getCode() const { return code_; }
private:
    int code_;
};

int main() {
    try {
        throw MyError(42);
    } catch (MyError &e) {
        std::cout << e.getCode() << std::endl;
    }
    return 0;
}
