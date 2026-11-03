class Base {
public:
    virtual ~Base() = default;
};

class Derived : protected Base {
public:
    void f() {}
};

int main() {
    Derived d;
    d.f();
    return 0;
}
