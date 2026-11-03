#include <iostream>

class Counter {
public:
    int value = 0;
    bool isZero() const {
        return value == 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-12-1]
    }
};

int main() {
    Counter c;
    std::cout << c.isZero() << std::endl;
    return 0;
}
