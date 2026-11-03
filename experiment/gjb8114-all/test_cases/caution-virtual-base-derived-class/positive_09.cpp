struct Base {
    int value = 0;
};

int main() {
    class Derived : public Base {
    public:
        int read() const { return value; }
    };

    Derived d;
    return d.read();
}
