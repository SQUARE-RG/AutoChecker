#include <iostream>

struct Flag {
    bool value;
};

bool operator&&(const Flag& lhs, const Flag& rhs) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-3]
    return lhs.value && rhs.value;
}

int main() {
    Flag a{true};
    Flag b{false};
    bool result = a && b;
    std::cout << result << '\n';
    return 0;
}
