#include <iostream>

union MixedValue {
    int i;
    double d;
};

class Engine {
public:
    Engine() : power(10) {}
    int power;
};

int main() {
    MixedValue m;
    m.i = 42;
    MixedValue *mp = &m;
    Engine *e = reinterpret_cast<Engine*>(mp); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-1]
    std::cout << e << std::endl;
    return 0;
}
