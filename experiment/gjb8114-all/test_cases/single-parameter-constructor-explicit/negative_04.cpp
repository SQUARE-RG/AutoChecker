#include <iostream>

template <typename T>
class Box {
public:
    Box(T v) : value(v) {} // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-3]
    T get() const { return value; }
private:
    T value;
};

template <typename T>
void printBox(const Box<T>& b) {
    std::cout << b.get() << std::endl;
}

int main() {
    Box<int> b = 10;
    printBox(b);
    return 0;
}
