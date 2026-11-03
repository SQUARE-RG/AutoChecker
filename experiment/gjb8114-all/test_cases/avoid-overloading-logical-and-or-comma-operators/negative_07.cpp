#include <iostream>

template <typename T>
class BoolLike {
public:
    explicit BoolLike(bool value) : value_(value) {}
    bool value() const { return value_; }

    // Overload logical AND in a class template.
    bool operator&&(const BoolLike& other) const {   // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-3]
        return value_ && other.value_;
    }

private:
    bool value_;
};

int main() {
    BoolLike<int> a(true);
    BoolLike<int> b(false);
    bool result = a && b;
    std::cout << result << '\n';
    return 0;
}
