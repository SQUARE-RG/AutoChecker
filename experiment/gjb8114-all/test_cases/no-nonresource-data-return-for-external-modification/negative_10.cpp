class Counter {
public:
    explicit Counter(int v) : value(v) {}
    decltype(auto) get() { return (value); } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-3]
private:
    int value;
};

int main() {
    Counter c(3);
    int& r = c.get();
    r = 7;
    return 0;
}
