struct Base {
    int value = 0;
};

int main() {
    class Derived : virtual public Base { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-1-1]
    public:
        int read() const { return value; }
    };

    Derived d;
    return d.read();
}
