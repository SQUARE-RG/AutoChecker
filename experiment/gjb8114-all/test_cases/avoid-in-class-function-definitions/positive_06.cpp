#include <iostream>

class Outer {
public:
    class Inner {
    public:
        int compute() const;
    };
};

int Outer::Inner::compute() const { return 1; }

int main() {
    Outer::Inner inner;
    std::cout << inner.compute() << '\n';
    return 0;
}
