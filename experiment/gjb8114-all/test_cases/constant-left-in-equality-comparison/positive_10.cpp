#include <iostream>

class Counter {
public:
    int value = 0;
    bool isZero() const {
        return 0 == value;
    }
};

int main() {
    Counter c;
    std::cout << c.isZero() << std::endl;
    return 0;
}
