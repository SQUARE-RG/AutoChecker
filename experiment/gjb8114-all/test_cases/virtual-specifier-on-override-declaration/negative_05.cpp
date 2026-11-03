class Base {
public:
    virtual int value() const { return 1; }
};

class Middle : public Base {
public:
    virtual int value() const override { return 2; }
};

class Derived : public Middle {
public:
    int value() const { return 3; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-2]
};

int main() {
    Derived d;
    const Base& b = d;
    return b.value() == 3 ? 0 : 1;
}
