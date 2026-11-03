#include <iostream>

template <typename T>
class CommaWrapper {
public:
    explicit CommaWrapper(T value) : value_(value) {}
    T value() const { return value_; }

    friend CommaWrapper operator,(const CommaWrapper& lhs, const CommaWrapper& rhs) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-3]
        return CommaWrapper(rhs.value_);
    }

private:
    T value_;
};

int main() {
    CommaWrapper<int> a(1);
    CommaWrapper<int> b(2);
    auto result = (a, b);
    std::cout << result.value() << '\n';
    return 0;
}
