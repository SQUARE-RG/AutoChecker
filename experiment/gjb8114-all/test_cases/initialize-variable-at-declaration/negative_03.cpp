class Temperature {
public:
    Temperature() {
        celsius_ = 0;
    }

    void set(int c) { celsius_ = c; }
    int get() const { return celsius_; }

private:
    int celsius_;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-1]
};

int main() {
    Temperature t;
    t.set(25);
    return t.get() == 25 ? 0 : 1;
}
