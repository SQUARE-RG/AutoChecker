struct Outer {
    template <typename T>
    struct Inner {
        T value;
    };
};

int main() {
    Outer::Inner<int> i{42};
    (void)i;
    return 0;
}
