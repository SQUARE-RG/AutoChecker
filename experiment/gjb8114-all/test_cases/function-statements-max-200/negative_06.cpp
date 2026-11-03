class BigDestructor {
public:
    BigDestructor() : counter(0) {}

    // CHECK-MESSAGES: :[[@LINE+1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-2-2]
    ~BigDestructor() {
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

private:
    int counter;
};

int main() {
    BigDestructor instance;
    return 0;
}
