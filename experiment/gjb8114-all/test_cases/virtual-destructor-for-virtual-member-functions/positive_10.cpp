#include <iostream>

class Outer {
public:
    class Inner {
    public:
        virtual void run();
        virtual ~Inner();
    };
};

void Outer::Inner::run() {
    std::cout << "run\n";
}

Outer::Inner::~Inner() {}

int main() {
    Outer::Inner inner;
    inner.run();
    return 0;
}
