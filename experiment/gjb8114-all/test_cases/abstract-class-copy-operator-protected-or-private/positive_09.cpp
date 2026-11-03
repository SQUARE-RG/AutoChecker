class B {
public:
    virtual ~B() = default;
    virtual void f() = 0;
protected:
    void operator=(B const& rhs) {
        kind = rhs.kind;
    }
private:
    int kind = 0;
};
