#include <iostream>

struct Gate {
    bool open;

    bool operator&&(const Gate& other) const { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-3]
        return open ? other.open : false;
    }
};

int main() {
    Gate a{true};
    Gate b{true};
    bool both = a && b;
    return both ? 0 : 1;
}
