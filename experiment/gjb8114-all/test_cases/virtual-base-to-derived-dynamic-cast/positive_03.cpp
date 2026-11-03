class B {
public:
    B() : b(1) {}
    virtual ~B() {}
    virtual int g(int a = 0) { return a + b; }
private:
    int b;
};

class D : public virtual B {
public:
    D() : B(), d(2) {}
    virtual ~D() {}
    int g(int a = 0) override { return a + d; }
private:
    int d;
};

int main() {
    D d;
    B *pb = &d;
    D *pd = dynamic_cast<D *>(pb);
    if (pd != nullptr) {
        pd->g();
    }
    return 0;
}
