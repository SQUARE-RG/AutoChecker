#include <iostream>

class Outer {
public:
    class Inner {
    public:
        int compute() const { return 1; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-7-1]
    };
};

int main() {
    Outer::Inner inner;
    std::cout << inner.compute() << '\n';
    return 0;
}
