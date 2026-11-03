class Base {
public:
    virtual ~Base() = default;
    virtual int value() & { return 7; }
};

class Derived : public Base {
public:
    virtual ~Derived() = default;
    int value() & { return 8; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-2]
};

int main() {
    Derived d;
    Base& b = d;
    return b.value();
}
