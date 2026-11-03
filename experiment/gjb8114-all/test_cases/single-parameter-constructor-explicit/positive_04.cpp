#include <iostream>

template <typename T>
class Box {
public:
    explicit Box(T v) : value(v) {}
    T get() const { return value; }
private:
    T value;
};

template <typename T>
void printBox(const Box<T>& b) {
    std::cout << b.get() << std::endl;
}

int main() {
    Box<int> b(10);
    printBox(b);
    return 0;
}
