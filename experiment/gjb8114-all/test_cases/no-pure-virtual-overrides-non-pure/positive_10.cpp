#include <cstddef>

class Base {
public:
    virtual void start() {}
    virtual ~Base() = default;
};

class Derived : public Base {
public:
    virtual void stop() = 0;
};

int main() {
    return 0;
}
