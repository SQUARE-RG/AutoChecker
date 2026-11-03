struct Outer {
    struct Base {
        virtual void bar() {}
    };
    struct Derived : Base {
        virtual void bar() = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-3]
    };
};

int main() {
    return 0;
}
