#include <iostream>

class Counter {
public:
    Counter() : current_(0), total_(0) {}
    explicit Counter(int start) : current_(start) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-4]
        if (start < 0) {
            current_ = 0;
        }
    }
    int current() const { return current_; }
    int total() const { return total_; }
private:
    int current_;
    int total_;
};

int main() {
    Counter first;
    Counter second(5);
    std::cout << first.current() << ' ' << second.current() << std::endl;
    return 0;
}
