class Base {
public:
    virtual int query(int value = 7) const;
    virtual ~Base() = default;
};

int Base::query(int value) const {
    return value + 1;
}

class Derived : public Base {
public:
    int query(int input = 7) const override;
};

int Derived::query(int input) const {
    return input + 2;
}

int main() {
    Derived d;
    Base& b = d;
    int r1 = b.query();
    int r2 = d.query();
    return r1 + r2;
}
