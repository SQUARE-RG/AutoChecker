class Counter {
public:
    explicit Counter(int initial = 0) : value_(initial) {}

    int* const raw() { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-3]
        return &value_;
    }

private:
    int value_;
};

int main() {
    Counter counter{1};
    int* const exposed = counter.raw();
    *exposed = 7;
    return 0;
}
