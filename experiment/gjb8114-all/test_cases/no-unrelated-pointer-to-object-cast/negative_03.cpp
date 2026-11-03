#include <iostream>
using namespace std;

struct S {
    int i;
    int j;
};

class C {
public:
    C() : i(0) {}
    void set(int v) { i = v; }
    int i;
};

int main() {
    C* c = new C();
    c->set(1);
    S* s = reinterpret_cast<S*>(c); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-1]
    s->i = 2;
    delete c;
    return 0;
}
