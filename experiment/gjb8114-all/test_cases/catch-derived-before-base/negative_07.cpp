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
    catch (Base<int>& e) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-1]
        std::cout << e.value << '\n';
    }
    catch (Derived& e) {
        std::cout << e.extra << '\n';
    }
    return 0;
}
