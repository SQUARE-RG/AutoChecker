#include <iostream>

class Counter {
public:
    Counter(int start) {}  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-2]

    int current() const { return 0; }
};

int main() {
    Counter counter(10);
    std::cout << counter.current() << std::endl;
    return 0;
}
