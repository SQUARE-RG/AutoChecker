#include <iostream>

class B {
private:
    int value = 1;
public:
    const int& get_value() const { return value; }
};

int main() {
    B b;
    const int& v = b.get_value();
    (void)v;
    return 0;
}
