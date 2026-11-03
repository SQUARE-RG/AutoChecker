#include <iostream>

enum class Mode { Slow, Fast };

class Base {
public:
    virtual ~Base() = default;
    virtual int schedule(Mode mode = Mode::Fast);
};

int Base::schedule(Mode mode) {
    return mode == Mode::Fast ? 1 : 0;
}

class Derived : public Base {
public:
    int schedule(Mode mode = Mode::Fast) override;
};

int Derived::schedule(Mode mode) {
    return mode == Mode::Fast ? 11 : 10;
}

int main() {
    Base base;
    Derived derived;
    Base &ref = derived;
    int x = base.schedule();
    int y = derived.schedule();
    int z = ref.schedule();
    std::cout << x + y + z << '\n';
    return 0;
}
