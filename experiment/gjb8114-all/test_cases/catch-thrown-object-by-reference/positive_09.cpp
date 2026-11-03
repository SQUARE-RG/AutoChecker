#include <iostream>

template <typename T>
class Error {
public:
    explicit Error(T v) : value(v) {}
    T get() const { return value; }
private:
    T value;
};

int main() {
    try {
        throw Error<int>(42);
    }
    catch (const Error<int>& e) {
        std::cout << e.get() << std::endl;
    }
    return 0;
}
