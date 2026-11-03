#include <cstddef>

class Base {
public:
    virtual void run() {}
    virtual ~Base() = default;
};

class Derived : public Base {
public:
    struct Task {
        virtual void run() = 0;
    };
};

int main() {
    return 0;
}
