struct Base {
    void baz() {}
};

struct Derived : Base {
    virtual void baz() = 0;
};

int main() {
    return 0;
}
