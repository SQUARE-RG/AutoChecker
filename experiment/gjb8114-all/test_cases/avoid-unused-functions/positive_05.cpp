class Calculator {
private:
    static int hidden_offset() {
        return 7;
    }

public:
    int value() const {
        return hidden_offset();
    }
};

int main() {
    Calculator calculator;
    return calculator.value();
}
