class Interface {
public:
    virtual void process(int value = 42) = 0;
    virtual ~Interface() = default;
};

class Implementation : public Interface {
public:
    void process(int value = 0) override; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-1]
};

void Implementation::process(int value) {
    (void)value;
}

int main() {
    Implementation impl;
    impl.process();
    return 0;
}
