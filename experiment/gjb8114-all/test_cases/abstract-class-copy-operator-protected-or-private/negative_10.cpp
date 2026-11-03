class B {
public:
    virtual ~B() = default;
    virtual void f() = 0;
    B& operator=(B const volatile& rhs); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-4]
private:
    int kind = 0;
};

B& B::operator=(B const volatile& rhs) {
    kind = rhs.kind;
    return *this;
}
