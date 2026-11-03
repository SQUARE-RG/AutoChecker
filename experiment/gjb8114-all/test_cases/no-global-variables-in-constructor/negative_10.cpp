#include <iostream>
int gValue = 42;
int* gPtr = &gValue;
class Foo {
public:
    Foo() {
        a = *gPtr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-1]
    }
private:
    int a;
};
int main() {
    Foo f;
    return 0;
}
