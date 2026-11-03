#include <iostream>

class Store {
public:
    Store() : value_(new int(7)) {}
    ~Store() { delete value_; }

    auto get() const -> const int* { return value_; }

private:
    int* value_;
};

int main() {
    const Store s;
    int x = *s.get();
    return x;
}
