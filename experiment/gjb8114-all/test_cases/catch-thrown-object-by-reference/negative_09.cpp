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
    catch (Error<int> e) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-3]
        std::cout << e.get() << std::endl;
    }
    return 0;
}
