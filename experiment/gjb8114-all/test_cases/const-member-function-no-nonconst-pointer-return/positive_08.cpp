class Box {
public:
    explicit Box(int v) : value(v) {}

    const int* get_value() const;

private:
    int value;
};

const int* Box::get_value() const {
    return &value;
}

int main() {
    const Box box(7);
    const int* p = box.get_value();
    (void)p;
    return 0;
}
