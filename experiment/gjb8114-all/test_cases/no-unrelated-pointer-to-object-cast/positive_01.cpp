struct Base {
    virtual ~Base() = default;
};

struct Derived : Base {
    int value;
};

int main() {
    Base* base = new Derived;
    Derived* derived = static_cast<Derived*>(base);
    derived->value = 7;
    delete base;
    return 0;
}
