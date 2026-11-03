#include <iostream>
#include <exception>

class MyError : public std::exception {
public:
    explicit MyError(int code) : code_(code) {}
    int getCode() const { return code_; }
    const char* what() const noexcept override { return "MyError"; }
private:
    int code_;
};

int main() {
    try {
        throw MyError(13);
    } catch (const MyError &e) {
        std::cout << e.getCode() << " " << e.what() << std::endl;
    }
    return 0;
}
