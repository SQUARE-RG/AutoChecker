class Flag {
public:
    Flag(bool value) : value_(value) {} // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-3]
    bool get() const { return value_; }
private:
    bool value_;
};

void take(Flag f) {
    (void)f;
}

int main() {
    Flag f = true;
    take(f);
    return 0;
}
