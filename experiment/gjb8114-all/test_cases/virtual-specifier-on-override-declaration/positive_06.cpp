class Base {
public:
    virtual int run() { return 1; }
};

class Derived : public Base {
public:
    virtual int run() final { return 2; }
};

int main() {
    Derived d;
    Base& b = d;
    return b.run() == 2 ? 0 : 1;
}
