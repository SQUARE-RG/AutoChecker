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
    D *pd = reinterpret_cast<D *>(pb); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-2]
    return (pd != nullptr) ? 0 : 1;
}
