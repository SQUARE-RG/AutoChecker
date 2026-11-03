#include <iostream>

template <typename T>
class Holder {
public:
    Holder() : value() {}
    ~Holder() { std::cout << 'x'; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-3-1]
    virtual void show(const T& v) { value = v; }
private:
    T value;
};

int main() {
    Holder<int> h;
    h.show(42);
    return 0;
}
