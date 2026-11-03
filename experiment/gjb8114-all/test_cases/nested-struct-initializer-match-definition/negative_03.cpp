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
    Outer value = {1, 2, 3, 4}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-3]
    return 0;
}
