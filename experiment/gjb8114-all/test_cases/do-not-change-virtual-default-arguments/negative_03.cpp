class Base {
public:
    virtual int calc(int x = 0, int y = 0) const;
    virtual ~Base() = default;
};

int Base::calc(int x, int y) const {
    return x + y;
}

class Derived : public Base {
public:
    int calc(int x = 0, int y = 1) const override; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-1]
};

int Derived::calc(int x, int y) const {
    return x + y + 10;
}

int main() {
    Derived d;
    Base& b = d;
    int r1 = b.calc();
    int r2 = d.calc();
    return r1 + r2;
}
