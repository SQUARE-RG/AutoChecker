class Base {
public:
    virtual ~Base() = default;
    virtual Base* clone() const { return nullptr; }
};

class Derived : public Base {
public:
    virtual ~Derived() = default;
    virtual Derived* clone() const { return nullptr; }
};

int main() {
    Derived d;
    Base& b = d;
    Base* p = b.clone();
    (void)p;
    return 0;
}
