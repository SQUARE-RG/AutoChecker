class Base {
public:
    virtual ~Base() = default;
    virtual int value() & { return 7; }
};

class Derived : public Base {
public:
    virtual ~Derived() = default;
    virtual int value() & { return 8; }
};

int main() {
    Derived d;
    Base& b = d;
    return b.value();
}
