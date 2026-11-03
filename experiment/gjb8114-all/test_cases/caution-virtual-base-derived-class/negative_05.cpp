class Base {
public:
    virtual ~Base() = default;
};

class Derived : virtual protected Base {  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-1-1]
public:
    void f() {}
};

int main() {
    Derived d;
    d.f();
    return 0;
}
