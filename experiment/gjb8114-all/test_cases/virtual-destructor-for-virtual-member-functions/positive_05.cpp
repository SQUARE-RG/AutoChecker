#include <iostream>

template <typename T>
class Holder {
public:
    Holder() : value() {}
    virtual ~Holder() { std::cout << 'x'; }
    virtual void show(const T& v) { value = v; }
private:
    T value;
};

int main() {
    Holder<int> h;
    h.show(42);
    return 0;
}
