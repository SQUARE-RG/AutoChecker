struct Base {
    int value = 0;
};

class Derived : Base {
public:
    int read() const { return value; }
};

int main() {
    Derived d;
    return d.read();
}
