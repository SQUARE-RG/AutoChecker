#include <iostream>

struct Accumulator {
    int total;

    Accumulator operator,(const Accumulator& other) const { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-3]
        return Accumulator{total + other.total};
    }
};

int main() {
    Accumulator a{1};
    Accumulator b{2};
    Accumulator c = (a, b);
    std::cout << c.total << '\n';
    return 0;
}
