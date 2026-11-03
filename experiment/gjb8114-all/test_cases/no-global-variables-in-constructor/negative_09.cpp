#include <iostream>
int gCounter = 0;
class Foo {
public:
    Foo();
private:
    int a;
};
Foo::Foo() {
    a = ++gCounter; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-1]
}
int main() {
    Foo f;
    std::cout << gCounter << std::endl;
    return 0;
}
