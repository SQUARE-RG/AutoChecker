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
    D* pd = dynamic_cast<D*>(pb);
    (void)pd;
    return 0;
}
