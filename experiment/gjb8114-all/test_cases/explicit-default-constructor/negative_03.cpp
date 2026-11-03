class CopyOnly { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-2]
public:
    CopyOnly(const CopyOnly& other) : value_(other.value_) {}
    int value() const { return value_; }
private:
    int value_;
};

int main() {
    return 0;
}
