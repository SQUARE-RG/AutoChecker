#include <iostream>

class Counter {
public:
    Counter(int start = 0) : value(start) {} // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-3]
    int get() const { return value; }
private:
    int value;
};

void consume(Counter c) {
    std::cout << c.get() << std::endl;
}

int main() {
    Counter c = 42;
    consume(7);
    return 0;
}
