#include <iostream>

class Counter {
public:
    Counter() {
        current_ = 0;
        total_ = 0;
    }
    explicit Counter(int start) {
        current_ = start;
        total_ = start < 0 ? 0 : start;
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
    std::cout << first.current() << first.total() << ' '
              << second.current() << second.total() << std::endl;
    return 0;
}
