struct A {
    int a;
    explicit A(int v) : a(v) {}
};

struct B {
    int b;
    B() : b(0) {}
};

struct Both : A, B {
    int value;
    Both() : A(1), value(2) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-5]
    {}
};

int main() {
    Both obj;
    return obj.value;
}
