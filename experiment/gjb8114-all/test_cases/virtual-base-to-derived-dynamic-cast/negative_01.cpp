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
    D* pd = reinterpret_cast<D*>(pb); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-2]
    (void)pd;
    return 0;
}
