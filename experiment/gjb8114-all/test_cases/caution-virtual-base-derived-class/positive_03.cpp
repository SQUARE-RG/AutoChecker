struct A { int a = 1; };
struct B { int b = 2; };

class Derived : public A, public B {
public:
    int value() const { return a + b; }
};

int main() {
    Derived d;
    return d.value();
}
