struct Base {
    virtual void g() = 0;
    virtual ~Base() = default;
};

struct Derived : Base {
    virtual void g(int) = 0;
};

int main() {
    Base* p = nullptr;
    return 0;
}
