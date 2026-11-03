class Base {
public:
    virtual ~Base() = default;
};

class Derived : public Base {};

int main() {
    try {
        throw new Derived();
    } catch (Base* b) {
        delete b;
    }
    return 0;
}
