struct Base {
    virtual void f() & {}
    virtual ~Base() = default;
};

struct Derived : Base {
    virtual void f() && = 0;
};

int main() {
    Base b;
    b.f();
    return 0;
}
