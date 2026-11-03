struct Outer {
    struct Middle {
        template <typename T>
        struct Inner {};
    };
};

int main() {
    Outer::Middle::Inner<int> value;
    (void)value;
    return 0;
}
