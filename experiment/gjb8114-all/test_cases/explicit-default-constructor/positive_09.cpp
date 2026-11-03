#include <iostream>

class Counter {
public:
    Counter();
    explicit Counter(int start);
    int value() const;
    void increment();
private:
    int value_ = 0;
};

Counter::Counter() = default;

Counter::Counter(int start) : value_(start) {}

int Counter::value() const {
    return value_;
}

void Counter::increment() {
    ++value_;
}

int main() {
    Counter c;
    c.increment();
    std::cout << c.value() << '\n';
    return 0;
}
