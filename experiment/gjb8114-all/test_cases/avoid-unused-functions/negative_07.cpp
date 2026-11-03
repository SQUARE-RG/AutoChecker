namespace {

template <typename T>
class Box {
public:
    explicit Box(T value) : value_(value) {}

    T value() const {
        return value_;
    }

    void unused_member() { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-3]
        value_ += T{1};
    }

private:
    T value_;
};

} // namespace

int main() {
    Box<int> b(3);
    (void)b.value();
    return 0;
}
