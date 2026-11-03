class Base {
public:
    virtual ~Base() = default;
    virtual int compute(int x) = 0;
};

class Derived : public Base {
public:
    virtual int compute(int x) override;
};

int Derived::compute(int x) {
    return x * 2;
}

int main() {
    Derived d;
    Base& b = d;
    return b.compute(3);
}
