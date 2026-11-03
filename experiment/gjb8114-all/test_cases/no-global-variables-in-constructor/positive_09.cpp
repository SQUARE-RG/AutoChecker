#include <iostream>
int gValue = 10;
class Foo {
public:
    Foo(int v) {
        a = ([v]() { return v * 2; })();
    }
private:
    int a;
};
int main() {
    Foo f(gValue);
    return 0;
}
