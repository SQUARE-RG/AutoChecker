#include <iostream>

class A {
private:
    int n = 1;
public:
    int get_n() const { return n; }
};

int main() {
    A a;
    int x = a.get_n();
    (void)x;
    return 0;
}
