struct Outer {
    template <class T>  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-1]
    struct Inner {
        T value;
    };
};

int main() {
    Outer::Inner<int> i{42};
    (void)i;
    return 0;
}
