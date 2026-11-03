class BraceInit {
private:
    int a;
    int b;
public:
    BraceInit() : a{0}, b{0} {}
};

int main() {
    BraceInit value;
    (void)value;
    return 0;
}
