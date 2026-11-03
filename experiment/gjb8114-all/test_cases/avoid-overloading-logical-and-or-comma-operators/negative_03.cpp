#include <iostream>

struct Flag {
    bool value;
};

bool operator||(const Flag& lhs, const Flag& rhs) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-3]
    return lhs.value ? true : rhs.value;
}

int main() {
    Flag a{true};
    Flag b{false};
    bool result = a || b;
    return result ? 0 : 1;
}
