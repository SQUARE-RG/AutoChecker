#include <cstdbool>

class Base {
public:
    int base_value(int x) const {
        return x + 1;
    }
};

class Derived : public Base {
public:
    int transformed(int x) const {
        return base_value(x) * 2;
    }

    int entry(int x) const {
        return transformed(x);
    }
};

int main() {
    Derived d;
    int value = d.entry(4);
    return value == 10 ? 0 : 1;
}
