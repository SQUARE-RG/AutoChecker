struct Base {
    virtual void qux() {}
};

struct Derived : Base {
    virtual void qux() const = 0;
};

int main() {
    return 0;
}
