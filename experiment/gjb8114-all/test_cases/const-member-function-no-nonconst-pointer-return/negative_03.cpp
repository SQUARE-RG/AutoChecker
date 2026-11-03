#include <iostream>

class Store {
public:
    Store() : value_(new int(7)) {}
    ~Store() { delete value_; }

    auto get() const -> int* { return value_; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-2]

private:
    int* value_;
};

int main() {
    const Store s;
    *s.get() = 42;
    return 0;
}
