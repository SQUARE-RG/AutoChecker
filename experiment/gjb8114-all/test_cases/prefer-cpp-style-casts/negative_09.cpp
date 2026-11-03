struct Base {
    int value;
};

struct Derived : Base {
    int extra;
};

int main() {
    Derived d;
    Base& b = (Base&)d; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-5-1]
    return b.value;
}
