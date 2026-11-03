#include <iostream>

class Outer {
public:
    class Inner {
    public:
        virtual void run();
        ~Inner(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-3-1]
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
