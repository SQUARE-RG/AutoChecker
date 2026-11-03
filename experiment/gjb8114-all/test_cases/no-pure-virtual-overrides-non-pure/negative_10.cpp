#include <cstddef>

template <typename T>
class Base {
public:
    virtual void process(T value) {}
    virtual ~Base() = default;
};

class Derived : public Base<int> {
public:
    virtual void process(int value) = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-3]
};

int main() {
    return 0;
}
