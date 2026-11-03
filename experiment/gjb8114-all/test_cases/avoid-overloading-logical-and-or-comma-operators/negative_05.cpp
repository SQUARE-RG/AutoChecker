#include <iostream>

struct Flag {
    bool value;
    explicit Flag(bool v) : value(v) {}

    bool operator||(const Flag& other) const { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-3]
        return value || other.value;
    }
};

int main() {
    Flag a(true);
    Flag b(false);
    bool result = a || b;
    std::cout << result << '\n';
    return 0;
}
