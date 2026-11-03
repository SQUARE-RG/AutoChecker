struct Outer {
    int o;
    struct Middle {
        int m;
        struct Inner {
            int a;
            int b;
        } inner;
    } middle;
};

int main() {
    Outer value = {1, {2, {3, 4}}};
    return 0;
}
