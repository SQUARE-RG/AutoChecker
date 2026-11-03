class Base {
public:
    virtual ~Base() = default;
    virtual const char* tag(const char* prefix = "stable") const { return prefix; }
};

class Derived : public Base {
public:
    const char* tag(const char* value = "stable") const override;
};

const char* Derived::tag(const char* value) const {
    return value;
}

int main() {
    Derived d;
    const char* result = d.tag();
    (void)result;
    return 0;
}
