struct A { int a = 1; };
struct B { int b = 2; };

class Derived : public A, public virtual B {  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-1-1]
public:
    int value() const { return a + b; }
};

int main() {
    Derived d;
    return d.value();
}
