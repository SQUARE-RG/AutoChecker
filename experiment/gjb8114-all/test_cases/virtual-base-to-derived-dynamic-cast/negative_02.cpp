#include <iostream>
using namespace std;
class B {
public:
    virtual ~B() {}
};
class D : public virtual B {
public:
    int value = 7;
};
int main() {
    D d;
    B* pb = &d;
    B& rb = *pb;
    D& rd = reinterpret_cast<D&>(rb); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-2]
    (void)rd;
    return 0;
}
