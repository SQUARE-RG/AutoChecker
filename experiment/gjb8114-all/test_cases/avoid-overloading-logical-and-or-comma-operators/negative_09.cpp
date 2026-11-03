#include <iostream>

class Flag {
public:
    explicit Flag(bool value) : value_(value) {}
    bool value() const { return value_; }

    friend bool operator||(const Flag& lhs, const Flag& rhs) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-3]
        return lhs.value_ || rhs.value_;
    }

private:
    bool value_;
};

int main() {
    Flag a(true);
    Flag b(false);
    bool result = a || b;
    std::cout << result << '\n';
    return 0;
}
