#include <iostream>

struct S {
    int i;
};

int main() {
    S s{7};
    const S* cp = &s;
    S* p = const_cast<S*>(cp);
    p->i = 8;
    std::cout << p->i << std::endl;
    return 0;
}
