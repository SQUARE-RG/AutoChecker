#include <iostream>

template <typename T>
class Base {
public:
    explicit Base(T v = T()) : value(v) {}
    virtual ~Base() = default;
    T value;
};

class Derived : public Base<int> {
public:
    explicit Derived(int v = 0) : Base<int>(v), extra(v * 2) {}
    int extra;
};

int main() {
    try {
        throw Derived(7);
    }
    catch (Derived& e) {
        std::cout << e.extra << '\n';
    }
    catch (Base<int>& e) {
        std::cout << e.value << '\n';
    }
    return 0;
}
