struct Calculator {
    static int add(int a, int b) {
        return a + b;
    }
};

int main() {
    return Calculator::add(3, 4);
}
