#include <iostream>

/* A class that demonstrates standard C block comments on access specifiers. */
class Counter {
public: /* public interface */
    int increment(int value) {
        return value + 1;
    }

private: /* internal state */
    int count = 0;

public: /* accessor for stored state */
    int getCount() const {
        return count;
    }
};

int main() {
    Counter counter;
    std::cout << counter.getCount() << std::endl;
    return 0;
}
