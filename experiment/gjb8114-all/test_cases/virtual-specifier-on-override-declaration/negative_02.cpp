class Base {
public:
    virtual ~Base() = default;
    virtual int compute(int x) = 0;
};

class Derived : public Base {
public:
    int compute(int x) override; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-2]
};

int Derived::compute(int x) {
    return x * 2;
}

int main() {
    Derived d;
    Base& b = d;
    return b.compute(3);
}
