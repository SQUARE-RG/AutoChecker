#include <iostream>

class Counter {
public:
    explicit Counter(int start) : value_(start) {}

    int current() const { return value_; }

private:
    int value_;
};

int main() {
    Counter counter(10);
    std::cout << counter.current() << std::endl;
    return 0;
}
