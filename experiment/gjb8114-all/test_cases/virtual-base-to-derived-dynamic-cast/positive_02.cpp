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
    D& rd = dynamic_cast<D&>(rb);
    (void)rd;
    return 0;
}
