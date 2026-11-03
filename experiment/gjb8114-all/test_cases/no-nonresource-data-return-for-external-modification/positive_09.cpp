class IntBox {
public:
    explicit IntBox(int v) : value(v) {}
    operator int() const { return value; }
private:
    int value;
};

int main() {
    IntBox box(3);
    int x = box;
    x = 7;
    return 0;
}
