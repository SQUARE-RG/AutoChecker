#include <iostream>

class Value {
public:
    explicit Value(int v) : v_(v) {}
    int value() const { return v_; }

    bool operator==(const Value& other) const { return v_ == other.v_; }
    bool operator<(const Value& other) const { return v_ < other.v_; }
    Value operator+(const Value& other) const { return Value(v_ + other.v_); }

private:
    int v_;
};

bool isBetween(const Value& x, const Value& low, const Value& high) {
    // Built-in && combines comparison results; && is not overloaded.
    return (low < x) && (x < high);
}

int main() {
    Value a(5), low(1), high(10);
    bool ok = isBetween(a, low, high) && (a + low).value() > 0;
    std::cout << ok << '\n';
    return 0;
}
