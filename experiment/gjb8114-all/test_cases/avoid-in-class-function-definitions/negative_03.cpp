#include <iostream>

class Counter {
public:
    Counter(int start) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-7-1]
        value = start;
    }

    int get() const;

private:
    int value;
};

int Counter::get() const {
    return value;
}

int main() {
    Counter c(5);
    std::cout << c.get() << std::endl;
    return 0;
}
