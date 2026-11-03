class Base {
public:
    Base() : id_(0) {}
    explicit Base(int id) : id_(id) {}
    int id_;
};

class Derived : public Base {
public:
    int value = 1;

    Derived() : Base(42) {}
};

int main() {
    Derived d;
    return 0;
}
