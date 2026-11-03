struct Outer {
    template <typename T>
    struct Level2 {
        struct Level3 {
            struct Level4 {}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-5]
        };
    };
};

int main() {
    Outer::Level2<int> value;
    (void)value;
    return 0;
}
