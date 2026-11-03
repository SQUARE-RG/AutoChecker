class Base {
public:
    virtual ~Base() = default;
    virtual int value(int x = 0) const { return x; }
};

class Derived : public Base {
public:
    virtual int value(int x = 0) const;
};

int Derived::value(int x) const {
    return x + 1;
}

int main() {
    Derived d;
    const Base& b = d;
    return b.value();
}
