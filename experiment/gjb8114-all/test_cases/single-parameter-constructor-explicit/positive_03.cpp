#include <iostream>

class Counter {
public:
    explicit Counter(int start = 0) : value(start) {}
    int get() const { return value; }
private:
    int value;
};

void consume(Counter c) {
    std::cout << c.get() << std::endl;
}

int main() {
    Counter c(42);
    consume(Counter(7));
    return 0;
}
