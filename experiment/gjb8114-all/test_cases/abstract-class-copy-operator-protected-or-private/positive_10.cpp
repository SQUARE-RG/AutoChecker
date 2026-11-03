class B {
public:
    virtual ~B() = default;
    virtual void f() = 0;
private:
    B& operator=(B& rhs) {
        kind = rhs.kind;
        return *this;
    }
    int kind = 0;
};
