class Box {
public:
    explicit Box(int v) : value(v) {}

    int* get_value() const; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-2]

private:
    int value;
};

int* Box::get_value() const {
    return const_cast<int*>(&value);
}

int main() {
    Box box(7);
    *box.get_value() = 11;
    return 0;
}
