union UnionWrapper {
    struct Outer {
        struct Level1 {
            struct Level2 {
                int value;
            };
        };
    };
    int dummy;
};

int main() {
    return 0;
}
