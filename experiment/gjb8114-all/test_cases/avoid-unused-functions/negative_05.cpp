class Calculator {
private:
    static int hidden_offset() { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-3]
        return 7;
    }

public:
    int value() const {
        return 42;
    }
};

int main() {
    Calculator calculator;
    return calculator.value();
}
