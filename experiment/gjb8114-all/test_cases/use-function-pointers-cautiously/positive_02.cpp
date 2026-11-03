#include <iostream>

class Operation {
public:
    virtual ~Operation() = default;
    virtual int apply(int value) const = 0;
};

class Increment final : public Operation {
public:
    int apply(int value) const override {
        return value + 1;
    }
};

int main() {
    Increment increment;
    const Operation& operation = increment;
    std::cout << operation.apply(4) << '\n';
    return 0;
}
