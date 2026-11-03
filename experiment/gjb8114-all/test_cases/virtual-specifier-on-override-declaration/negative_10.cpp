class Base {
public:
    virtual ~Base() = default;
    virtual Base* clone() const { return nullptr; }
};

class Derived : public Base {
public:
    virtual ~Derived() = default;
    Derived* clone() const { return nullptr; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-2]
};

int main() {
    Derived d;
    Base& b = d;
    Base* p = b.clone();
    (void)p;
    return 0;
}
