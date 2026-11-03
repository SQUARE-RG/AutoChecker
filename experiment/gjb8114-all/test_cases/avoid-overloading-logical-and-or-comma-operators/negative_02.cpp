#include <iostream>

struct Pair {
    int value;
};

int operator,(const Pair& lhs, const Pair& rhs) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-3]
    return lhs.value + rhs.value;
}

int main() {
    Pair first{10};
    Pair second{20};
    int sum = (first, second);
    std::cout << sum << '\n';
    return 0;
}
