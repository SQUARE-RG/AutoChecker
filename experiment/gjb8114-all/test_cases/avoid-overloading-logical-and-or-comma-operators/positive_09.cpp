#include <iostream>

class Flag {
public:
    explicit Flag(bool value) : value_(value) {}
    bool value() const { return value_; }

private:
    bool value_;
};

bool either(const Flag& lhs, const Flag& rhs) {
    if (lhs.value()) {
        return true;
    }
    return rhs.value();
}

int main() {
    Flag a(true);
    Flag b(false);
    bool result = either(a, b);
    std::cout << result << '\n';
    return 0;
}
