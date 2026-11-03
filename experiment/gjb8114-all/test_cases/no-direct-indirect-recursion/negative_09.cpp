#include <cstdbool>

class Parity {
public:
    bool is_even(int n) {
        if (n == 0) {
            return true;
        }
        return is_odd(n - 1); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-16]
    }

    bool is_odd(int n) {
        if (n == 0) {
            return false;
        }
        return is_even(n - 1);
    }
};

int main() {
    Parity p;
    bool result = p.is_even(0);
    return result ? 0 : 1;
}
