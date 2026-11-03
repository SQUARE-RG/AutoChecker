struct Base {
    int value;
};

struct Derived : Base {
    int extra;
};

int main() {
    Derived d;
    Base& b = static_cast<Base&>(d);
    return b.value;
}
