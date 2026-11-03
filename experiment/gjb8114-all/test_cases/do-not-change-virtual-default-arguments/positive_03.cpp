class Base {
public:
    virtual int compute(int a = 3, int b = 4) const;
    virtual ~Base() = default;
};

int Base::compute(int a, int b) const {
    return a * b;
}

class Derived : public Base {
public:
    int compute(int a = 3, int b = 4) const override;
};

int Derived::compute(int a, int b) const {
    return a * b + 1;
}

int main() {
    Derived d;
    Base& b = d;
    int r1 = b.compute();
    int r2 = d.compute();
    return r1 + r2;
}
