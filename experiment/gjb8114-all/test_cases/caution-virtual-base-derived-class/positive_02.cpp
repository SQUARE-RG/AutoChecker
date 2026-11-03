class Base {
public:
    virtual ~Base() = default;
};

struct Derived : Base {
    ~Derived() override = default;
};
