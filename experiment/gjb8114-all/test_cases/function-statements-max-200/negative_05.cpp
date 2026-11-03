class BigConstructor {
public:
    // CHECK-MESSAGES: :[[@LINE+1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-2-2]
    BigConstructor() : counter(0) {
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;

        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;

        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;

        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;

        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;

        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;

        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;

        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;

        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;

        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;

        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;

        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;

        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;

        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;

        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;

        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;

        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;

        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;

        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
        counter += 1;
    }

    int get() const {
        return counter;
    }

private:
    int counter;
};

int main() {
    BigConstructor instance;
    return instance.get();
}
