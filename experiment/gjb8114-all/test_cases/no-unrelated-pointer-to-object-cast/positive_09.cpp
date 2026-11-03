#include <iostream>

struct S {
    int i;
};

int main() {
    S s{42};
    void* v = &s;
    S* p = static_cast<S*>(v);
    std::cout << p->i << std::endl;
    return 0;
}
