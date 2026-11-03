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
    virtual int value() const { return 3; }
};

int main() {
    Derived d;
    const Base& b = d;
    return b.value() == 3 ? 0 : 1;
}
